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
from typing import Optional, Any, List, Literal
import json
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from agentstr.logger import get_logger

logger = get_logger(__name__)


class User(BaseModel):
    """Simple user model persisted by the database layer."""

    user_id: str
    available_balance: int = 0
    current_thread_id: str | None = None


class Message(BaseModel):
    """Chat/message row stored per agent/thread."""

    agent_name: str
    thread_id: str
    idx: int
    user_id: str
    role: Literal["user", "agent"]
    content: str
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

    # ------------------------------------------------------------------
    # Current thread ID helpers
    # ------------------------------------------------------------------
    @abc.abstractmethod
    async def get_current_thread_id(self, user_id: str) -> str | None:
        """Return the current thread id for *user_id* within this agent scope."""

    @abc.abstractmethod
    async def set_current_thread_id(self, user_id: str, thread_id: str | None) -> None:
        """Persist *thread_id* as the current thread for *user_id*."""

