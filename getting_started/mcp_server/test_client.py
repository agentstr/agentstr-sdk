
from dotenv import load_dotenv
load_dotenv()

import os
import json
from agentstr import NostrMCPClient, PrivateKey

server_public_key = os.getenv("NOSTR_PUBKEY")

async def chat():
    # Initialize the client
    mcp_client = NostrMCPClient(mcp_pubkey=server_public_key,
                                private_key=PrivateKey().bech32())

    # List available tools
    tools = await mcp_client.list_tools()
    print(f"Found tools: {json.dumps(tools, indent=4)}")

    # Call a tool
    result = await mcp_client.call_tool("add", {"a": 69, "b": 420})
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())
