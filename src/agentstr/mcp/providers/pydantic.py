from typing import Any, Union
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from pydantic_ai import Tool


async def to_pydantic_tools(nostr_mcp_client: NostrMCPClient) -> list[Tool]:
    """Convert tools from the MCP client to Pydantic tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of Pydantic tools that wrap the MCP tools.
    """

    def call_tool(
            tool_name: str,
    ):
        async def inner(arguments: dict[str, Any]):
            result = await nostr_mcp_client.call_tool(tool_name, arguments)
            return result
        return inner

    tools = await nostr_mcp_client.list_tools()
    tool_to_schema = {}
    for tool in tools["tools"]:
        tool_to_schema[tool["name"]] = {"type": "object", "properties": {"arguments": tool["inputSchema"]}, "required": ['arguments']}

    async def prepare_tool(ctx: RunContext[Any], tool_def: ToolDefinition) -> Union[ToolDefinition, None]:
        tool_def.parameters_json_schema = tool_to_schema.get(tool_def.name)
        return tool_def

    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            function=call_tool(tool["name"]),
            prepare=prepare_tool,
            takes_ctx=False,
        ) for tool in tools["tools"]
    ]
    