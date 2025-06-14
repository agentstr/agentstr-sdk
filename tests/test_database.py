import pytest
import pytest_asyncio
from agentstr.database import Database, User

@pytest_asyncio.fixture
async def db():
    database = Database('sqlite://:memory:')
    await database.async_init()
    yield database
    await database.close()

@pytest.mark.asyncio
async def test_user_model():
    user = User(user_id='u1', available_balance=42)
    assert user.user_id == 'u1'
    assert user.available_balance == 42
    # Default balance
    user2 = User(user_id='u2')
    assert user2.available_balance == 0

@pytest.mark.asyncio
async def test_get_user_not_found(db):
    user = await db.get_user('nonexistent')
    assert user.user_id == 'nonexistent'
    assert user.available_balance == 0

@pytest.mark.asyncio
async def test_upsert_and_get_user(db):
    user = User(user_id='alice', available_balance=100)
    await db.upsert_user(user)
    fetched = await db.get_user('alice')
    assert fetched.user_id == 'alice'
    assert fetched.available_balance == 100

@pytest.mark.asyncio
async def test_upsert_user_update(db):
    user = User(user_id='bob', available_balance=50)
    await db.upsert_user(user)
    # Update balance
    user2 = User(user_id='bob', available_balance=75)
    await db.upsert_user(user2)
    fetched = await db.get_user('bob')
    assert fetched.available_balance == 75

@pytest.mark.asyncio
async def test_ensure_user_table_idempotent(db):
    # Should not fail if called twice
    await db._ensure_user_table()
    await db._ensure_user_table()
