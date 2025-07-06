"""Simple Agentstr agent with payment processing."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent
import os

# Note: the NWC_CONN_STR environment variable is used by default for payment processing
if os.getenv("NWC_CONN_STR") is None:
    raise ValueError("NWC_CONN_STR environment variable is not set")

# Define the Nostr Agent Server
async def main():
    agent = AgentstrAgent(
        name="PaymentEnabledAgent",
        description="A simple Agentstr Agent with payment processing",
        satoshis=10,  # 10 sats per message
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
