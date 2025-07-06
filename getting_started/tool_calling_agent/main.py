"""Minimal Agentstr agent - says hello to users."""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from agentstr import AgentCard, NostrAgent, NostrAgentServer, ChatInput

# Define an agent callable
async def hello_world_agent(chat: ChatInput) -> str:
    return f"Hello {chat.user_id}!"

# Define the Nostr Agent
nostr_agent = NostrAgent(
    agent_card=AgentCard(
        name="HelloWorldAgent", 
        description="A minimal example that greets users.", 
    ),
    agent_callable=hello_world_agent
)

# Define the Nostr Agent Server
async def main():
    server = NostrAgentServer(nostr_agent)
    await server.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
