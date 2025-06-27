import os
import time
import pytest
from dotenv import load_dotenv
from pynostr.key import PrivateKey
from agentstr.relays import RelayManager

load_dotenv()

@pytest.mark.asyncio
async def test_send_receive_message():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]

    private_key1 = PrivateKey()
    private_key2 = PrivateKey()

    manager = RelayManager(relays, private_key1)
    manager2 = RelayManager(relays, private_key2)

    timestamp = int(time.time())
    await manager.send_message("hello", private_key2.public_key.hex())

    dm_event = await manager2.receive_message(private_key1.public_key.hex(), timestamp)

    assert dm_event.message == "hello"
