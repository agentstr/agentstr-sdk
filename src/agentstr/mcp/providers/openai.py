import json
from typing import Any

from agents import RunContextWrapper, FunctionTool

from agentstr.mcp.nostr_mcp_client import NostrMCPClient


async def to_openai_tools(nostr_mcp_client: NostrMCPClient) -> list[FunctionTool]:
    """Convert tools from the MCP client to OpenAI tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of OpenAI FunctionTool objects that wrap the MCP tools.
    """
    
    tools = await nostr_mcp_client.list_tools()

    def call_tool(
            tool_name: str,
    ):
        async def inner(ctx: RunContextWrapper[Any], args: str):
            result = await nostr_mcp_client.call_tool(tool_name, json.loads(args))
            return result
        return inner

    return [
        FunctionTool(
            name=tool["name"],
            description=tool["description"],
            params_json_schema=tool["inputSchema"],
            on_invoke_tool=call_tool(tool["name"]),
        )
        for tool in tools["tools"]
    ]