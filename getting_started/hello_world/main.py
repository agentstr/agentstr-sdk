"""Minimal Agentstr agent - says hello to users."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent, ChatInput


# Define an agent callable
async def hello_world_agent(chat: ChatInput) -> str:
    return f"Hello {chat.user_id}!"


# Define the Agent
async def main():
    agent = AgentstrAgent(
        name="HelloWorldAgent",
        description="A minimal example that greets users.",
        agent_callable=hello_world_agent,
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
