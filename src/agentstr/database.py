import aiosqlite
import asyncio
from typing import Optional
from pydantic import BaseModel
from agentstr.logger import get_logger

logger = get_logger(__name__)


class User(BaseModel):
    user_id: str
    available_balance: int = 0

class Database:
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or 'sqlite://agentstr_local.db'
        self._is_sqlite = self.connection_string.startswith('sqlite://')
        self.conn = None  # Will be set in async_init

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def async_init(self):
        if self._is_sqlite:
            db_path = self.connection_string.replace('sqlite://', '', 1)
            self.conn = await aiosqlite.connect(db_path)
        else:
            raise NotImplementedError("Only SQLite is supported in this implementation.")
        await self._ensure_user_table()
        return self

    async def _ensure_user_table(self):
        async with self.conn.execute(
            '''CREATE TABLE IF NOT EXISTS user (
                user_id TEXT PRIMARY KEY,
                available_balance INTEGER NOT NULL
            )'''
        ):
            pass
        await self.conn.commit()

    async def get_user(self, user_id: str) -> User:
        logger.debug(f"Getting user: {user_id}")
        async with self.conn.execute(
            'SELECT available_balance FROM user WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                logger.debug(f"User {user_id} found with balance {row[0]}")
                return User(user_id=user_id, available_balance=row[0])
            else:
                logger.debug(f"User {user_id} not found")
                return User(user_id=user_id)

    async def upsert_user(self, user: User):
        logger.debug(f"Upserting user: {user}")
        await self.conn.execute(
            '''INSERT INTO user (user_id, available_balance) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET available_balance=excluded.available_balance''',
            (user.user_id, user.available_balance)
        )
        await self.conn.commit()
