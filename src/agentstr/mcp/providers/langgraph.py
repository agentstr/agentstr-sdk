from typing import Any

from langchain_core.tools import BaseTool, StructuredTool, ToolException
from mcp.types import (
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    TextContent,
)

from agentstr.mcp.nostr_mcp_client import NostrMCPClient

NonTextContent = ImageContent | EmbeddedResource



def _convert_call_tool_result(
    call_tool_result: CallToolResult,
) -> tuple[str | list[str], list[NonTextContent] | None]:
    """Convert a CallToolResult into a format suitable for LangGraph tools.

    Args:
        call_tool_result: The result from calling an MCP tool.

    Returns:
        A tuple containing:
        - The tool's output as a string or list of strings
        - A list of non-text content (images, embedded resources) or None

    Raises:
        ToolException: If the tool call resulted in an error.
    """
    text_contents: list[TextContent] = []
    non_text_contents = []
    for content in call_tool_result.content:
        if isinstance(content, TextContent):
            text_contents.append(content)
        else:
            non_text_contents.append(content)

    tool_content: str | list[str] = [content.text for content in text_contents]
    if not text_contents:
        tool_content = ""
    elif len(text_contents) == 1:
        tool_content = tool_content[0]

    if call_tool_result.isError:
        raise ToolException(tool_content)

    return tool_content


async def to_langgraph_tools(nostr_mcp_client: NostrMCPClient) -> list[BaseTool]:
    """Convert tools from the MCP client to LangGraph tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of LangGraph BaseTool objects that wrap the MCP tools.
    """
    # Load tools from this server
    tools = await nostr_mcp_client.list_tools()
    server_tools = []

    def call_tool(
            tool_name: str,
    ):
        async def inner(**arguments: dict[str, Any]):
            call_tool_result = await nostr_mcp_client.call_tool(tool_name, arguments)
            call_tool_result = CallToolResult(**call_tool_result)
            result = _convert_call_tool_result(call_tool_result)
            return result
        return inner

    for tool in tools["tools"]:
        server_tools.append(
            StructuredTool(
                name=tool["name"],
                description=tool.get("description") or "",
                metadata={"satoshis": tool.get("satoshis", 0)},
                args_schema=tool["inputSchema"],
                coroutine=call_tool(tool["name"]),
                response_format="content",
            ),
        )
    return server_tools
