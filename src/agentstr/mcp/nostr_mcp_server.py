import asyncio
import json
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools.tool_manager import ToolManager
from pynostr.event import Event
from agentstr.models import Tool, Metadata
from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient
from agentstr.utils import stringify_result

logger = get_logger(__name__)


def tool(**kwargs):
    """Decorator to mark a function as a tool with extra parameters for registration via add_tool.

    Usage:
        @tool(name="mytool", description="desc", satoshis=100)
        def myfunc(...): ...

    The parameters are attached to the function as __tool_params__.
    """
    def decorator(fn):
        setattr(fn, "__tool_params__", kwargs)
        return fn
    return decorator


class NostrMCPServer:
    """Server for exposing tools over Nostr as a Model Context Protocol (MCP) server.

    Listens for tool requests, executes them, and returns results, optionally charging 
    via Nostr Wallet Connect (NWC). Most arguments are optional as they can be set via 
    environment variables like `NOSTR_NSEC` for private key, `NOSTR_RELAYS` for relay URLs, 
    and `NWC_CONN_STR` for Nostr Wallet Connect string. See the documentation for more 
    details on environment variable usage.
    """
    def __init__(self, display_name: str | None = None, nostr_client: NostrClient | None = None,
                 relays: list[str] | None = None, private_key: str | None = None, nwc_str: str | None = None,
                 tools: list[Callable[..., Any]] = [], nostr_metadata: Metadata | None = None):
        """Initialize the MCP server.

        Args:
            display_name: Display name of the server.
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            tools: List of tools to register (optional).
            nostr_metadata: Nostr metadata for the server (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.display_name = display_name
        self.nostr_metadata = nostr_metadata
        self.tool_to_sats_map = {}
        self.tool_manager = ToolManager()
        for tool in tools:
            self.add_tool(tool)

    def add_tool(self, fn: Callable[..., Any], name: str | None = None,
                 description: str | None = None, satoshis: int | None = None):
        """Register a tool with the server.

        Args:
            fn: The function to register as a tool.
            name: Name of the tool (defaults to function name).
            description: Description of the tool (optional).
            satoshis: Satoshis required to call the tool (optional).
        """
        tool_params = getattr(fn, "__tool_params__", None)
        if tool_params:
            name = name or tool_params.get("name")
            description = description or tool_params.get("description")
            satoshis = satoshis or tool_params.get("satoshis")
        if satoshis:
            self.tool_to_sats_map[name or fn.__name__] = satoshis
        self.tool_manager.add_tool(fn=fn, name=name, description=description)

    async def list_tools(self) -> dict[str, Any]:
        """List all registered tools and their metadata.

        Returns:
            Dictionary containing a list of tools with their names, descriptions,
            input schemas, and required satoshis.
        """
        return {
            "tools": [{
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters,
                "satoshis": self.tool_to_sats_map.get(tool.name, 0),
            } for tool in self.tool_manager.list_tools()],
        }

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str | None:
        """Execute a registered tool by name with provided arguments.

        Args:
            name: Name of the tool to call.
            arguments: Dictionary of arguments for the tool.

        Returns:
            Result of the tool execution.

        Raises:
            ToolError: If the tool is not found.
        """
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        tool = self.tool_manager.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")
        result = await tool.fn(**arguments)
        logger.info(f"Tool call result: {result}")
        if result is None:
            return None
        return stringify_result(result)

    async def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages to process tool calls or list requests.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        message = message.strip()
        logger.debug(f"Request: {message}")
        tasks = []
        try:
            request = json.loads(message)
            if request["action"] == "list_tools":
                response = await self.list_tools()
            elif request["action"] == "call_tool":
                tool_name = request["tool_name"]
                arguments = request["arguments"]
                satoshis = self.tool_to_sats_map.get(tool_name, 0)
                if satoshis > 0:
                    invoice = await self.client.nwc_relay.make_invoice(amount=satoshis, description=f"Payment for {tool_name} tool")
                    response = invoice

                    async def on_success():
                        logger.info(f"Payment succeeded for {tool_name}")
                        result = await self.call_tool(tool_name, arguments)
                        response = {"content": [{"type": "text", "text": result}]}
                        logger.debug(f"On success response: {response}")
                        await self.client.send_direct_message(event.pubkey, json.dumps(response))

                    async def on_failure():
                        response = {"error": f"Payment failed for {tool_name}"}
                        logger.error(f"On failure response: {response}")
                        await self.client.send_direct_message(event.pubkey, json.dumps(response))

                    # Run in background
                    tasks.append(asyncio.create_task(
                        self.client.nwc_relay.on_payment_success(
                            invoice=invoice,
                            callback=on_success,
                            unsuccess_callback=on_failure,
                            timeout=900,
                        ),
                    ))
                else:
                    result = await self.call_tool(tool_name, arguments)
                    response = {"content": [{"type": "text", "text": str(result)}]}
            else:
                response = {"error": f"Invalid action: {request['action']}"}
        except Exception as e:
            response = {"content": [{"type": "text", "text": str(e)}]}
        if not isinstance(response, str):
            response = json.dumps(response)
        logger.debug(f"MCP Server response: {response}")
        tasks.append(self.client.send_direct_message(event.pubkey, response))
        await asyncio.gather(*tasks)

    async def start(self):
        """Start the MCP server, updating metadata and listening for direct messages."""
        logger.info(f"Updating metadata for {self.client.public_key.bech32()}")
        await self.client.update_metadata(
            name="mcp_server",
            display_name=self.display_name,
            about=json.dumps(await self.list_tools()),
            nostr_metadata=self.nostr_metadata,
        )
        logger.info(f"Starting message listener for {self.client.public_key.bech32()}")
        await self.client.direct_message_listener(callback=self._direct_message_callback)
