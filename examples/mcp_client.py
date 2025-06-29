from dotenv import load_dotenv

load_dotenv()

import json
import os

from agentstr import NostrMCPClient

# Define relays and private key
relays   = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("MCP_CLIENT_NSEC")

# To enable Nostr Wallet Connect
nwc_str = os.getenv("MCP_CLIENT_NWC_CONN_STR")

# Define MCP server public key
server_public_key = os.getenv("MCP_SERVER_PUBKEY")


async def run()   :
    # Initialize the client
    mcp_client = NostrMCPClient(mcp_pubkey=server_public_key,
                                relays=relays,
                                private_key=private_key,
                                nwc_str=nwc_str)

    # List available tools
    tools = await mcp_client.list_tools()
    print(f"Found tools: {json.dumps(tools, indent=4)}")

    # Call a tool
    result = await mcp_client.call_tool("add", {"a": 69, "b": 420})
    print(f'The result of 69 + 420 is: {result["content"][-1]["text"]}')

    # Call a premium tool
    result = await mcp_client.call_tool("multiply", {"a": 69, "b": 420})
    print(f'The result of 69 * 420 is: {result["content"][-1]["text"]}')

    # Call a premium tool
    result = await mcp_client.call_tool("get_weather", {"city": "San Francisco"})
    print(f'The weather in San Francisco is: {result["content"][-1]["text"]}')


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
