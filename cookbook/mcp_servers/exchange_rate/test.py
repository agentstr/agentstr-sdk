import dotenv

dotenv.load_dotenv()

from agentstr import NostrMCPClient
from pynostr.key import PrivateKey
import os
import json


# Define relays and private key
relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = PrivateKey().bech32()

# Define MCP server public key
server_public_key = 'npub1qg6xyneg439778thgg3xnf66ldkfrnly52yl2f4pvwnypqsh650qp8kdms'


async def run():
    # Initialize the client
    mcp_client = NostrMCPClient(mcp_pubkey=server_public_key, relays=relays, private_key=private_key)

    # List available tools
    tools = await mcp_client.list_tools()
    print(f'Found tools: {json.dumps(tools, indent=4)}')

    # Call a tool
    result = await mcp_client.call_tool("get_exchange_rate", {"currency_from": "USD", "currency_to": "EUR"})
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    