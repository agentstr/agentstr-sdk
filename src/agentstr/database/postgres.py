import asyncpg
import json
from datetime import datetime, timezone
from typing import Self, Any, List, Literal

from agentstr.models import Message, User
from agentstr.database.base import BaseDatabase
from agentstr.logger import get_logger

logger = get_logger(__name__)


class PostgresDatabase(BaseDatabase):
    """PostgreSQL implementation using `asyncpg`."""

    USER_TABLE_NAME = "agentstr_users"
    MESSAGE_TABLE_NAME = "agentstr_messages"

    def __init__(self, conn_str: str, *, agent_name: str | None = None):
        super().__init__(conn_str, agent_name)

    async def async_init(self) -> Self:
        logger.debug("Connecting to Postgres: %s", self.conn_str)
        self.conn = await asyncpg.connect(dsn=self.conn_str)
        await self._ensure_user_table()
        await self._ensure_message_table()
        return self

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    # --------------------------- helpers -------------------------------
    async def _ensure_user_table(self) -> None:
        await self.conn.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.USER_TABLE_NAME} (
                agent_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                available_balance INTEGER NOT NULL,
                current_thread_id TEXT,
                PRIMARY KEY (agent_name, user_id)
            )"""
        )
        # Index for agent filtering
        await self.conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.USER_TABLE_NAME}_agent_name ON {self.USER_TABLE_NAME} (agent_name)"
        )

    async def _ensure_message_table(self) -> None:
        """Create message table if it doesn't exist."""
        await self.conn.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.MESSAGE_TABLE_NAME} (
                agent_name TEXT NOT NULL,
                thread_id  TEXT NOT NULL,
                idx        INTEGER NOT NULL,
                user_id    TEXT NOT NULL,
                role       TEXT NOT NULL,
                message    TEXT,
                content    TEXT NOT NULL,
                kind       TEXT,
                satoshis   INTEGER,
                extra_inputs   TEXT,
                extra_outputs  TEXT,

                created_at TIMESTAMP NOT NULL,
                PRIMARY KEY (agent_name, thread_id, idx, user_id)
            )""",
        )
        await self.conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.MESSAGE_TABLE_NAME}_thread ON {self.MESSAGE_TABLE_NAME} (agent_name, thread_id)"
        )
        await self.conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self.MESSAGE_TABLE_NAME}_user ON {self.MESSAGE_TABLE_NAME} (agent_name, user_id)"
        )

    async def add_message(
        self,
        thread_id: str,
        user_id: str,
        role: Literal["user", "agent", "tool"],
        message: str = "",
        content: str = "",
        kind: str = "request",
        satoshis: int | None = None,
        extra_inputs: dict[str, Any] = {},
        extra_outputs: dict[str, Any] = {},
    ) -> Message:
        next_idx: int = await self.conn.fetchval(
            f"SELECT COALESCE(MAX(idx), -1) + 1 FROM {self.MESSAGE_TABLE_NAME} WHERE agent_name = $1 AND thread_id = $2",
            self.agent_name,
            thread_id,
        )
        created_at = datetime.now(timezone.utc)
        await self.conn.execute(
            f"INSERT INTO {self.MESSAGE_TABLE_NAME} (agent_name, thread_id, idx, user_id, role, message, content, kind, satoshis, extra_inputs, extra_outputs, created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)",
            self.agent_name,
            thread_id,
            next_idx,
            user_id,
            role,
            message,
            content,
            kind,
            satoshis,
            json.dumps(extra_inputs) if extra_inputs else None,
            json.dumps(extra_outputs) if extra_outputs else None,
            created_at,
        )
        return Message(
            agent_name=self.agent_name,
            thread_id=thread_id,
            idx=next_idx,
            user_id=user_id,
            role=role,
            message=message,
            content=content,
            kind=kind,
            satoshis=satoshis,
            extra_inputs=extra_inputs,
            extra_outputs=extra_outputs,
            created_at=created_at.astimezone(timezone.utc),
        )

    async def get_messages(
        self,
        thread_id: str,
        user_id: str,
        *,
        limit: int | None = None,
        before_idx: int | None = None,
        after_idx: int | None = None,
        reverse: bool = False,
    ) -> List[Message]:
        """Retrieve messages for *thread_id* ordered by idx."""
        base_query = f"SELECT * FROM {self.MESSAGE_TABLE_NAME} WHERE agent_name = $1 AND thread_id = $2 AND user_id = $3"
        params: list[Any] = [self.agent_name, thread_id, user_id]
        param_pos = 4  # next positional argument index for $ placeholders
        if after_idx is not None:
            base_query += f" AND idx > ${param_pos}"
            params.append(after_idx)
            param_pos += 1
        if before_idx is not None:
            base_query += f" AND idx < ${param_pos}"
            params.append(before_idx)
            param_pos += 1
        order = "DESC" if reverse else "ASC"
        base_query += f" ORDER BY idx {order}"
        if limit is not None:
            base_query += f" LIMIT ${param_pos}"
            params.append(limit)
        rows = await self.conn.fetch(base_query, *params)
        return [Message.from_row(row) for row in rows]

    # --------------------------- API ----------------------------------

    # ------------------- thread helpers -------------------
    async def get_current_thread_id(self, user_id: str) -> str | None:
        """Return the current thread id for *user_id* within this agent scope."""
        user = await self.get_user(user_id)
        return user.current_thread_id

    async def set_current_thread_id(self, user_id: str, thread_id: str | None) -> None:
        """Persist *thread_id* as the current thread for *user_id*."""
        user = await self.get_user(user_id)
        user.current_thread_id = thread_id
        await self.upsert_user(user)

    # --------------------------- API ----------------------------------
    async def get_user(self, user_id: str) -> User:
        logger.debug("[Postgres] Getting user %s", user_id)
        row = await self.conn.fetchrow(
            f"SELECT available_balance, current_thread_id FROM {self.USER_TABLE_NAME} WHERE agent_name = $1 AND user_id = $2",
            self.agent_name,
            user_id,
        )
        if row:
            return User(user_id=user_id, available_balance=row["available_balance"], current_thread_id=row["current_thread_id"])
        return User(user_id=user_id)

    async def upsert_user(self, user: User) -> None:
        logger.debug("[Postgres] Upserting user %s", user)
        await self.conn.execute(
            f"""INSERT INTO {self.USER_TABLE_NAME} (agent_name, user_id, available_balance, current_thread_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (agent_name, user_id) DO UPDATE
            SET available_balance = EXCLUDED.available_balance, current_thread_id = EXCLUDED.current_thread_id""",
            self.agent_name,
            user.user_id,
            user.available_balance,
            user.current_thread_id,
        )
