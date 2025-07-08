import os
import pytest
from dotenv import load_dotenv

load_dotenv()

from agentstr.relays import NWCRelay

nwc_relay = NWCRelay(os.getenv("TEST_NWC_CONN_STR"))


@pytest.mark.asyncio
async def test_get_info():
    info = await nwc_relay.get_info()
    assert info["result"]["pubkey"]