import dspy
from typing import Any
from agentstr.mcp.nostr_mcp_client import NostrMCPClient


async def to_dspy_tools(nostr_mcp_client: NostrMCPClient) -> list[dspy.Tool]:
    """Convert tools from the MCP client to Dspy tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of DSPy Tool objects that wrap the MCP tools.
    """
    tools = await nostr_mcp_client.list_tools()

    def call_tool(
            tool_name: str,
    ):
        async def inner(**arguments: dict[str, Any]):
            result = await nostr_mcp_client.call_tool(tool_name, arguments)
            return result
        return inner

    return [dspy.Tool(
            name=tool["name"],
            desc=tool["description"],
            func=call_tool(tool["name"]),
        ) for tool in tools["tools"]]
