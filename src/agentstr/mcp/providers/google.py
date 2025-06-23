import json
from typing import Any
from typing_extensions import override

from google.genai.types import FunctionDeclaration
from google.adk.tools.base_tool import BaseTool
from google.adk.tools import ToolContext
from google.adk.tools.openapi_tool.openapi_spec_parser.rest_api_tool import to_gemini_schema

from agentstr.mcp.nostr_mcp_client import NostrMCPClient


class NostrMCPTool(BaseTool):
    def __init__(self, nostr_mcp_client: NostrMCPClient, tool: dict[str, Any]):
        super().__init__(
            name=tool["name"],
            description=tool["description"],
        )
        self.nostr_mcp_client = nostr_mcp_client
        self.tool = tool

    @override
    def _get_declaration(self) -> FunctionDeclaration:
        """Gets the function declaration for the tool.

        Returns:
            FunctionDeclaration: The Gemini function declaration for the tool.
        """
        schema_dict = self.tool['inputSchema']
        parameters = to_gemini_schema(schema_dict)
        function_decl = FunctionDeclaration(
            name=self.name, description=self.description, parameters=parameters
        )
        return function_decl

    async def run_async(self, *, args, tool_context: ToolContext):
        """Runs the tool asynchronously.

        Args:
            args: The arguments as a dict to pass to the tool.
            tool_context: The tool context from upper level ADK agent.

        Returns:
            Any: The response from the tool.
        """
        response = await self.nostr_mcp_client.call_tool(self.tool['name'], arguments=args)
        return response


async def to_google_tools(nostr_mcp_client: NostrMCPClient) -> list[BaseTool]:
    """Convert tools from the MCP client to Google tools.

    Args:
        nostr_mcp_client: An instance of NostrMCPClient to fetch tools from.

    Returns:
        A list of Google FunctionTool objects that wrap the MCP tools.
    """
    
    tools = await nostr_mcp_client.list_tools()

    return [
        NostrMCPTool(
            nostr_mcp_client=nostr_mcp_client,
            tool=tool,
        )
        for tool in tools["tools"]
    ]