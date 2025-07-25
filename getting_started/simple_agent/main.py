"""Simple Agentstr agent - pass-through LLM call."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent


# Define the Agent
async def main():
    agent = AgentstrAgent(
        name="SimpleAgent",
        description="A simple Agentstr Agent",
        prompt="You are a helpful assistant.",
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
