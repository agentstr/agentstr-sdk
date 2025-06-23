import os
from typing import Optional
from agentstr.database.sqlite import SQLiteDatabase
from agentstr.database.postgres import PostgresDatabase
from agentstr.database.base import BaseDatabase, User, Message
from agentstr.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------

def Database(connection_string: Optional[str] = None, *, agent_name: str = "default") -> BaseDatabase:
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
