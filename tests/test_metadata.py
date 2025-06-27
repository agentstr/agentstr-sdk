import os
import time
import pytest
from dotenv import load_dotenv
from pynostr.key import PrivateKey
from agentstr.relays import RelayManager

load_dotenv()

@pytest.mark.asyncio
async def test_set_and_get_following():
    relays = ['ws://localhost:6969']
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    # Set following to a known list
    following_list = ['pubkey1', 'pubkey2']
    await manager.set_following(pubkey, following_list)
    # Give relay time to process
    time.sleep(0.5)
    result = await manager.get_following(pubkey)
    assert set(result) == set(following_list)

@pytest.mark.asyncio
async def test_add_following():
    relays = ['ws://localhost:6969']
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    # Start with empty following
    await manager.set_following(pubkey, [])
    time.sleep(0.5)
    # Add one
    await manager.add_following(pubkey, ['pubkeyA'])
    time.sleep(0.5)
    result = await manager.get_following(pubkey)
    assert 'pubkeyA' in result
    # Add another, ensure both present
    await manager.add_following(pubkey, ['pubkeyB'])
    time.sleep(0.5)
    result = await manager.get_following(pubkey)
    assert set(result) == {'pubkeyA', 'pubkeyB'}

@pytest.mark.asyncio
async def test_add_following_no_duplicates():
    relays = ['ws://localhost:6969']
    private_key = PrivateKey()
    manager = RelayManager(relays, private_key)
    pubkey = private_key.public_key.hex()

    await manager.set_following(pubkey, ['pubkeyX'])
    time.sleep(0.5)
    await manager.add_following(pubkey, ['pubkeyX', 'pubkeyY'])
    time.sleep(0.5)
    result = await manager.get_following(pubkey)
    assert set(result) == {'pubkeyX', 'pubkeyY'}
