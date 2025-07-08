import os
import asyncio
import pytest
from dotenv import load_dotenv
from pynostr.key import PrivateKey
from agentstr.relays import RelayManager
from agentstr.nostr_client import NostrClient
from pynostr.metadata import Metadata

load_dotenv()

@pytest.mark.asyncio
async def test_set_and_get_following():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    pubkeyA = PrivateKey().public_key.hex()
    pubkeyB = PrivateKey().public_key.hex()

    # Set following to a known list
    following_list = [pubkeyA, pubkeyB]
    await manager.set_following(pubkey, following_list)
    # Give relay time to process
    await asyncio.sleep(0.5)
    result = await manager.get_following(pubkey)
    assert set(result) == set(following_list)

@pytest.mark.asyncio
async def test_add_following():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    pubkeyA = PrivateKey().public_key.hex()
    pubkeyB = PrivateKey().public_key.hex()
    # Start with empty following
    await manager.set_following(pubkey, [])
    await asyncio.sleep(1)
    # Add one
    await manager.add_following(pubkey, [pubkeyA])
    await asyncio.sleep(1)
    result = await manager.get_following(pubkey)
    assert pubkeyA in result
    # Add another, ensure both present
    await manager.add_following(pubkey, [pubkeyB])
    await asyncio.sleep(1)
    result = await manager.get_following(pubkey)
    assert set(result) == {pubkeyA, pubkeyB}

@pytest.mark.asyncio
async def test_add_following_no_duplicates():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    pubkeyX = PrivateKey().public_key.hex()
    pubkeyY = PrivateKey().public_key.hex()

    await manager.set_following(pubkey, [pubkeyX])
    await asyncio.sleep(1)
    await manager.add_following(pubkey, [pubkeyX, pubkeyY])
    await asyncio.sleep(1)
    result = await manager.get_following(pubkey)
    assert set(result) == {pubkeyX, pubkeyY}

@pytest.mark.asyncio
async def test_update_and_get_metadata():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]
    private_key = PrivateKey()
    client = NostrClient(relays, private_key.bech32())

    # Set initial metadata
    await client.update_metadata(name="Alice", about="Test user", picture="https://example.com/alice.png")
    await asyncio.sleep(1)
    meta = await client.get_metadata_for_pubkey()
    assert meta is not None
    assert meta.name == "Alice"
    assert meta.about == "Test user"
    assert meta.picture == "https://example.com/alice.png"

    # Update metadata, change only 'about' and add 'banner'
    await asyncio.sleep(1)
    await client.update_metadata(about="Updated bio", banner="https://example.com/banner.png")
    await asyncio.sleep(1)
    meta2 = await client.get_metadata_for_pubkey()
    assert meta2 is not None
    assert meta2.name == "Alice"  # unchanged
    assert meta2.about == "Updated bio"
    assert meta2.banner == "https://example.com/banner.png"

@pytest.mark.asyncio
async def test_update_metadata_with_metadata_obj():
    relays = [os.getenv("NOSTR_RELAYS", "ws://localhost:6969").split(",")[0]]
    private_key = PrivateKey()
    client = NostrClient(relays, private_key.bech32())

    # Use Metadata object
    meta_obj = Metadata()
    meta_obj.name = "Bob"
    meta_obj.about = "Bio for Bob"
    meta_obj.picture = "https://example.com/bob.jpg"
    await client.update_metadata(nostr_metadata=meta_obj)
    await asyncio.sleep(0)
    meta = await client.get_metadata_for_pubkey()
    assert meta is not None
    assert meta.name == "Bob"
    assert meta.about == "Bio for Bob"
    assert meta.picture == "https://example.com/bob.jpg"

