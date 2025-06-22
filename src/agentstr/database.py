"""Database abstraction layer with SQLite and Postgres implementations.

The module exposes a `Database` factory function that returns an instance of
`SQLiteDatabase` or `PostgresDatabase` depending on the provided connection
string.  Supported schemes are::

    sqlite://<path | :memory:>
    postgresql://<user>:<pass>@<host>:<port>/<dbname>
    postgres://<user>:<pass>@<host>:<port>/<dbname>

All implementations share the same async API.
"""
from __future__ import annotations

import abc
import os
from typing import Optional, Protocol, runtime_checkable, Any, List, Literal

import aiosqlite
import asyncpg
import json
from datetime import datetime
from pydantic import BaseModel, Field

from agentstr.logger import get_logger

logger = get_logger(__name__)


class User(BaseModel):
    """Simple user model persisted by the database layer."""

    user_id: str
    available_balance: int = 0


class Message(BaseModel):
    """Chat/message row stored per agent/thread."""

    agent_name: str
    thread_id: str
    idx: int
    user_id: str
    role: Literal["user", "agent"]
    content: str
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_row(cls, row: Any) -> "Message":  # helper for Sqlite (tuple) or asyncpg.Record
        if row is None:
            raise ValueError("Row cannot be None")
        # Both sqlite and pg rows behave like dicts with keys
        return cls(
            agent_name=row["agent_name"],
            thread_id=row["thread_id"],
            idx=row["idx"],
            user_id=row["user_id"],
            role=row["role"],
            content=row["content"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            created_at=row["created_at"],
        )

@runtime_checkable
class _DatabaseProtocol(Protocol):
    """Runtime protocol to help with type-checking and duck-typing."""

    async def async_init(self) -> "_DatabaseProtocol":
        ...

    async def close(self) -> None:
        ...

    async def get_user(self, user_id: str) -> "User":
        ...

    async def upsert_user(self, user: "User") -> None:
        ...

    async def add_message(
        self,
        thread_id: str,
        user_id: str,
        role: Literal["user", "agent"],
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> "Message":
        ...

    async def get_messages(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        before_idx: int | None = None,
        after_idx: int | None = None,
        reverse: bool = False,
    ) -> List["Message"]:
        ...


class BaseDatabase(abc.ABC):
    """Abstract base class for concrete database backends."""

    def __init__(self, connection_string: str, agent_name: str = "default"):
        self.connection_string = connection_string
        self.agent_name = agent_name
        self.conn = None  # Will be set by :py:meth:`async_init`.

    # ---------------------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------------------
    @abc.abstractmethod
    async def async_init(self) -> "BaseDatabase":
        """Perform any asynchronous initialisation required for the backend."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the underlying connection (if any)."""

    # ------------------------------------------------------------------
    # CRUD operations (synchronous wrappers around async where sensible)
    # ------------------------------------------------------------------
    @abc.abstractmethod
    async def get_user(self, user_id: str) -> "User":
        """Fetch a :class:`User` by *user_id*.  Non-existent users yield a
        default model with a zero balance."""

    @abc.abstractmethod
    async def upsert_user(self, user: "User") -> None:
        """Create or update *user* in storage atomically."""

    # ------------------------------------------------------------------
    # Message history operations
    # ------------------------------------------------------------------
    @abc.abstractmethod
    async def add_message(
        self,
        thread_id: str,
        user_id: str,
        role: Literal["user", "agent"],
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> "Message":
        """Append a message to a thread and return the stored model."""

    @abc.abstractmethod
    async def get_messages(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        before_idx: int | None = None,
        after_idx: int | None = None,
        reverse: bool = False,
    ) -> List["Message"]:
        """Retrieve messages for *thread_id* ordered by idx."""


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
            "SELECT available_balance FROM user WHERE agent_name = ? AND user_id = ?",
            (self.agent_name, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return User(user_id=user_id, available_balance=row[0])
            return User(user_id=user_id)  # default balance 0

    async def upsert_user(self, user: "User") -> None:
        logger.debug("[SQLite] Upserting user %s", user)
        await self.conn.execute(
            """INSERT INTO user (agent_name, user_id, available_balance) VALUES (?, ?, ?)
            ON CONFLICT(agent_name, user_id) DO UPDATE SET available_balance = excluded.available_balance""",
            (self.agent_name, user.user_id, user.available_balance),
        )
        await self.conn.commit()


class PostgresDatabase(BaseDatabase):
    """PostgreSQL implementation using `asyncpg`."""

    _TABLE_NAME = "agent_user"  # avoid reserved keyword "user"

    def __init__(self, connection_string: str, *, agent_name: str = "default"):
        super().__init__(connection_string, agent_name)

    async def async_init(self) -> "PostgresDatabase":
        logger.debug("Connecting to Postgres: %s", self.connection_string)
        self.conn = await asyncpg.connect(dsn=self.connection_string)
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
            f"""CREATE TABLE IF NOT EXISTS {self._TABLE_NAME} (
                agent_name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                available_balance INTEGER NOT NULL,
                PRIMARY KEY (agent_name, user_id)
            )"""
        )
        # Index for agent filtering
        await self.conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self._TABLE_NAME}_agent_name ON {self._TABLE_NAME} (agent_name)"
        )

    # --------------------------- API ----------------------------------
    async def get_user(self, user_id: str) -> "User":
        logger.debug("[Postgres] Getting user %s", user_id)
        row = await self.conn.fetchrow(
            f"SELECT available_balance FROM {self._TABLE_NAME} WHERE agent_name = $1 AND user_id = $2",
            self.agent_name,
            user_id,
        )
        if row:
            return User(user_id=user_id, available_balance=row["available_balance"])
        return User(user_id=user_id)

    async def upsert_user(self, user: "User") -> None:
        logger.debug("[Postgres] Upserting user %s", user)
        await self.conn.execute(
            f"""INSERT INTO {self._TABLE_NAME} (agent_name, user_id, available_balance)
            VALUES ($1, $2, $3)
            ON CONFLICT (agent_name, user_id) DO UPDATE
            SET available_balance = EXCLUDED.available_balance""",
            self.agent_name,
            user.user_id,
            user.available_balance,
        )


# ---------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------

def Database(connection_string: Optional[str] = None, *, agent_name: str = "default") -> _DatabaseProtocol:
    """Factory returning an appropriate database backend instance.

    Examples
    --------
    >>> db = Database("sqlite://:memory:")
    >>> db = await db.async_init()
    """

    # Check env var first if no connection string supplied
    env_conn = os.getenv("DATABASE_URL")
    conn_str = connection_string or env_conn or "sqlite://agentstr_local.db"
    if conn_str.startswith("sqlite://"):
        logger.info("Using SQLite backend")
        return SQLiteDatabase(conn_str, agent_name=agent_name)
    if conn_str.startswith("postgres://") or conn_str.startswith("postgresql://"):
        conn_str = conn_str.replace("postgresql://", "postgres://", 1)
        logger.info("Using Postgres backend")
        return PostgresDatabase(conn_str, agent_name=agent_name)
    raise ValueError(f"Unsupported connection string: {conn_str}")


__all__ = [
    "User",
    "Database",
    "Message",
    "SQLiteDatabase",
    "PostgresDatabase",
]
