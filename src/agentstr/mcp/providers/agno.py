from typing import Any

from agno.tools import Function

from agentstr.nostr_mcp_client import NostrMCPClient


async def to_agno_tools(nostr_mcp_client: NostrMCPClient) -> list[Function]:
    """Convert tools from the MCP client to Agno tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of Agno Function objects that wrap the MCP tools.
    """
    tools = await nostr_mcp_client.list_tools()

    def call_tool(
            tool_name: str,
    ):
        async def inner(arguments: dict[str, Any]) -> dict[str, Any]:
            result = await nostr_mcp_client.call_tool(tool_name, arguments)
            return result
        return inner

    return [Function(
            name=tool["name"],
            description=tool["description"],
            parameters={"type": "object", "properties": {"arguments": tool["inputSchema"]}, "required": ['arguments']},
            entrypoint=call_tool(tool["name"]),
        ) for tool in tools["tools"]]
