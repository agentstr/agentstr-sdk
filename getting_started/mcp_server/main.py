"""Simple MCP Server"""

from dotenv import load_dotenv
load_dotenv()

import os
from agentstr import NostrMCPServer, tool

# Addition tool
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Multiplication tool
@tool(satoshis=0)
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Weather tool (premium tool)
@tool(satoshis=5)
async def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


async def run():
    # Define the server
    server = NostrMCPServer(
        "SimpleMCPServer",
        nwc_str=os.getenv("NWC_CONN_STR"),
        tools=[add, multiply, get_weather],
    )

    # Start the server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())


