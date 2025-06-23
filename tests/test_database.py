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


# -----------------------------------------------------------------------------
# Message history API tests
# -----------------------------------------------------------------------------
from agentstr.database import Message  # noqa: E402 - import after top-level for tests

@pytest.mark.asyncio
async def test_add_and_get_messages(db):
    # Add two messages to a new thread and verify ordering / indices
    m1 = await db.add_message(
        thread_id="thread1",
        user_id="u1",
        role="user",
        content="Hello",
        metadata={"foo": "bar"},
    )
    assert isinstance(m1, Message)
    assert m1.idx == 0
    assert m1.metadata == {"foo": "bar"}

    m2 = await db.add_message(
        thread_id="thread1",
        user_id="u1",
        role="agent",
        content="Hi there!",
    )
    assert m2.idx == 1

    messages = await db.get_messages("thread1")
    assert [m.idx for m in messages] == [0, 1]
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there!"


@pytest.mark.asyncio
async def test_get_messages_pagination(db):
    # populate
    for i in range(5):
        await db.add_message(
            thread_id="thread2",
            user_id="u1",
            role="user" if i % 2 == 0 else "agent",
            content=str(i),
        )

    # Limit
    latest_two = await db.get_messages("thread2", limit=2, reverse=True)
    assert [m.idx for m in latest_two] == [4, 3]

    # after_idx
    after1 = await db.get_messages("thread2", after_idx=1)
    assert [m.idx for m in after1] == [2, 3, 4]

    # before_idx
    before4 = await db.get_messages("thread2", before_idx=4)
    assert [m.idx for m in before4] == [0, 1, 2, 3]

    # Combined limit + reverse
    single = await db.get_messages("thread2", limit=1, reverse=True)
    assert single[0].idx == 4


@pytest.mark.asyncio
async def test_current_thread_id_default_none(db):
    user_id = "ctid1"
    user = await db.get_user(user_id)
    assert user.current_thread_id is None
    ctid = await db.get_current_thread_id(user_id)
    assert ctid is None

@pytest.mark.asyncio
async def test_set_and_get_current_thread_id(db):
    user_id = "ctid2"
    thread_id = "threadX"
    await db.set_current_thread_id(user_id, thread_id)
    ctid = await db.get_current_thread_id(user_id)
    assert ctid == thread_id
    # Should persist on user fetch
    user = await db.get_user(user_id)
    assert user.current_thread_id == thread_id

@pytest.mark.asyncio
async def test_update_current_thread_id(db):
    user_id = "ctid3"
    thread_id1 = "threadA"
    thread_id2 = "threadB"
    await db.set_current_thread_id(user_id, thread_id1)
    assert await db.get_current_thread_id(user_id) == thread_id1
    await db.set_current_thread_id(user_id, thread_id2)
    assert await db.get_current_thread_id(user_id) == thread_id2

@pytest.mark.asyncio
async def test_set_current_thread_id_to_none(db):
    user_id = "ctid4"
    thread_id = "threadZ"
    await db.set_current_thread_id(user_id, thread_id)
    assert await db.get_current_thread_id(user_id) == thread_id
    await db.set_current_thread_id(user_id, None)
    assert await db.get_current_thread_id(user_id) is None
