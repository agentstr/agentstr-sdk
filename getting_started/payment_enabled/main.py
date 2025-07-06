"""Simple Agentstr agent with payment processing."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent, NostrClient
import os


# Define the Nostr Agent Server
async def main():
    agent = AgentstrAgent(
        name="PaymentEnabledAgent",
        description="A simple Agentstr Agent with payment processing",
        satoshis=10,  # 10 sats per message
        nostr_client=NostrClient(nwc_str=os.getenv("NWC_CONN_STR"))
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
