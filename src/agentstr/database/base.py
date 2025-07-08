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
from typing import Any, List, Literal
from agentstr.models import Message, User

from agentstr.logger import get_logger

logger = get_logger(__name__)


class BaseDatabase(abc.ABC):
    """Abstract base class for concrete database backends."""

    def __init__(self, conn_str: str, agent_name: str | None = None):
        self.conn_str = conn_str
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
        role: Literal["user", "agent", "tool"],
        message: str = "",
        content: str = "",
        kind: str = "request",
        satoshis: int | None = None,
        extra_inputs: dict[str, Any] = {},
        extra_outputs: dict[str, Any] = {},
    ) -> "Message":
        """Append a message to a thread and return the stored model."""

    @abc.abstractmethod
    async def get_messages(
        self,
        thread_id: str,
        user_id: str,
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

