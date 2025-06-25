import asyncio
import os
import uuid
import time

from dotenv import load_dotenv

load_dotenv()

from pynostr.key import PrivateKey

from agentstr.relay_manager import RelayManager


async def test_relay_manager():
    relays = os.getenv("NOSTR_RELAYS").split(",")

    private_key1 = PrivateKey()
    private_key2 = PrivateKey()

    manager = RelayManager(relays, private_key1)
    manager2 = RelayManager(relays, private_key2)

    timestamp = int(time.time())
    event = await manager.send_message("hello", private_key2.public_key.hex())
    print(event)

    dm_event = await manager2.receive_message(private_key1.public_key.hex(), timestamp)
    print(dm_event)

    assert dm_event.message == "hello"

async def test_relay_manager_message_tags():
    relays = os.getenv("NOSTR_RELAYS").split(",")

    private_key1 = PrivateKey()
    private_key2 = PrivateKey()
    thread_id = uuid.uuid4().hex

    manager = RelayManager(relays, private_key1)
    manager2 = RelayManager(relays, private_key2)

    timestamp = int(time.time())
    event = await manager.send_message("hello", private_key2.public_key.hex(), tags={"t": [thread_id, 'test']})
    print(event)

    dm_event = await manager2.receive_message(private_key1.public_key.hex(), timestamp)
    assert dm_event.event.get_tag_dict().get("t")[0][0] == thread_id
    assert dm_event.event.get_tag_dict().get("t")[0][1] == 'test'
    print(dm_event)

    assert dm_event.message == "hello"

async def test_get_following():
    relays = os.getenv("NOSTR_RELAYS").split(",")
    private_key = PrivateKey.from_nsec(os.getenv("AGENT_PRIVATE_KEY"))
    manager = RelayManager(relays, private_key)
    following = await manager.get_following()
    print("Following")
    print(following)


async def test_suite():
    await test_relay_manager()
    await test_relay_manager_message_tags()
    await test_get_following()


if __name__ == "__main__":
    asyncio.run(test_suite())
