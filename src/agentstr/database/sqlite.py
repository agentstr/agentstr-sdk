from typing import Optional, Any, List, Literal
import json
import aiosqlite
from datetime import datetime, timezone

from agentstr.database.base import BaseDatabase, User, Message
from agentstr.logger import get_logger

logger = get_logger(__name__)


class SQLiteDatabase(BaseDatabase):
    """SQLite implementation using `aiosqlite`."""

    def __init__(self, connection_string: Optional[str] = None, *, agent_name: str = "default"):
        super().__init__(connection_string or "sqlite://agentstr_local.db", agent_name)
        # Strip the scheme to obtain the filesystem path.
        self._db_path = self.connection_string.replace("sqlite://", "", 1)

    # --------------------------- helpers -------------------------------
    async def _ensure_user_table(self) -> None:
        async with self.conn.execute(
            """CREATE TABLE IF NOT EXISTS user (
                agent_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                available_balance INTEGER NOT NULL,
                current_thread_id TEXT,
                PRIMARY KEY (agent_name, user_id)
            )"""
        ):
            pass
        # Index on agent_name for faster agent filtering
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_agent_name ON user (agent_name)"
        )
        await self.conn.commit()

    async def _ensure_message_table(self) -> None:
        async with self.conn.execute(
            """CREATE TABLE IF NOT EXISTS message (
                agent_name TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                idx INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME NOT NULL,
                PRIMARY KEY (agent_name, thread_id, idx)
            )"""
        ):
            pass
        # Index on agent_name for faster agent filtering
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_message_agent_name ON message (agent_name)"
        )
        # Index on thread_id for faster thread filtering
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_message_thread_id ON message (thread_id)"
        )
        await self.conn.commit()

    # --------------------------- API ----------------------------------
    async def async_init(self) -> "SQLiteDatabase":
        self.conn = await aiosqlite.connect(self._db_path)
        # Return rows as mappings so we can access by column name
        self.conn.row_factory = aiosqlite.Row
        await self._ensure_user_table()
        await self._ensure_message_table()
        return self

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def get_user(self, user_id: str) -> "User":
        logger.debug("[SQLite] Getting user %s", user_id)
        async with self.conn.execute(
            "SELECT available_balance, current_thread_id FROM user WHERE agent_name = ? AND user_id = ?",
            (self.agent_name, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return User(user_id=user_id, available_balance=row[0], current_thread_id=row[1])
            return User(user_id=user_id)

    async def get_current_thread_id(self, user_id: str) -> str | None:
        """Return the current thread id for *user_id* within this agent scope."""
        user = await self.get_user(user_id)
        return user.current_thread_id

    async def set_current_thread_id(self, user_id: str, thread_id: str | None) -> None:
        """Persist *thread_id* as the current thread for *user_id*."""
        user = await self.get_user(user_id)
        user.current_thread_id = thread_id
        await self.upsert_user(user)


    async def upsert_user(self, user: "User") -> None:
        logger.debug("[SQLite] Upserting user %s", user)
        await self.conn.execute(
            """INSERT INTO user (agent_name, user_id, available_balance, current_thread_id) VALUES (?, ?, ?, ?)
            ON CONFLICT(agent_name, user_id) DO UPDATE SET available_balance = excluded.available_balance, current_thread_id = excluded.current_thread_id""",
            (self.agent_name, user.user_id, user.available_balance, user.current_thread_id),
        )
        await self.conn.commit()

    async def add_message(
            self,
            thread_id: str,
            user_id: str,
            role: Literal["user", "agent"],
            content: str,
            metadata: dict[str, Any] | None = None,
        ) -> "Message":
            """Append a message to a thread and return the stored model."""
            metadata_json = json.dumps(metadata or {}) if metadata else None
            # Determine next index for thread
            async with self.conn.execute(
                "SELECT COALESCE(MAX(idx), -1) + 1 AS next_idx FROM message WHERE agent_name = ? AND thread_id = ?",
                (self.agent_name, thread_id),
            ) as cursor:
                row = await cursor.fetchone()
                next_idx = row[0]

            created_at = datetime.now(timezone.utc).isoformat()
            await self.conn.execute(
                "INSERT INTO message (agent_name, thread_id, idx, user_id, role, content, metadata, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (
                    self.agent_name,
                    thread_id,
                    next_idx,
                    user_id,
                    role,
                    content,
                    metadata_json,
                    created_at,
                ),
            )
            await self.conn.commit()
            return Message(
                agent_name=self.agent_name,
                thread_id=thread_id,
                idx=next_idx,
                user_id=user_id,
                role=role,
                content=content,
                metadata=metadata,
                created_at=datetime.fromisoformat(created_at).astimezone(timezone.utc),
            )

    async def get_messages(
            self,
            thread_id: str,
            *,
            limit: int | None = None,
            before_idx: int | None = None,
            after_idx: int | None = None,
            reverse: bool = False,
    ) -> List["Message"]:
        """Retrieve messages for *thread_id* with optional pagination."""
        query = "SELECT * FROM message WHERE agent_name = ? AND thread_id = ?"
        params: list[Any] = [self.agent_name, thread_id]
        if after_idx is not None:
                query += " AND idx > ?"
                params.append(after_idx)
        if before_idx is not None:
                query += " AND idx < ?"
                params.append(before_idx)
        order = "DESC" if reverse else "ASC"
        query += f" ORDER BY idx {order}"
        if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
        async with self.conn.execute(query, tuple(params)) as cursor:
                rows = await cursor.fetchall()
        return [Message.from_row(dict(r)) for r in rows]
