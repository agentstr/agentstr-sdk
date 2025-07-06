"""Agentstr agent with payment processing and tool calling."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent
import os

# Note: the NWC_CONN_STR environment variable is used by default for payment processing
if os.getenv("NWC_CONN_STR") is None:
    raise ValueError("NWC_CONN_STR environment variable is not set")

# Note: make sure MCP_SERVER_PUBKEY is set
if os.getenv("MCP_SERVER_PUBKEY") is None:
    raise ValueError("MCP_SERVER_PUBKEY environment variable is not set")

# Define the Nostr Agent Server
async def main():
    agent = AgentstrAgent(
        name="PaymentEnabledAgent",
        description="A simple Agentstr Agent with payment processing",
        satoshis=0,  # 0 sats per message
        nostr_mcp_pubkeys=[os.getenv("MCP_SERVER_PUBKEY")],
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
