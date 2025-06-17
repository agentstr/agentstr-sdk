import json
import time
from typing import Any

from pynostr.utils import get_public_key

from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient

logger = get_logger(__name__)


class NostrMCPClient:
    """Client for interacting with Model Context Protocol (MCP) servers on Nostr.

    Discovers and calls tools from MCP servers, handling payments via NWC when needed.

    Examples
    --------
    Basic usage demonstrating listing tools and calling one::

        import asyncio
        from agentstr import NostrMCPClient

        relays = ["wss://relay.damus.io"]
        mcp_client = NostrMCPClient(
            mcp_pubkey="npub1example...",  # MCP server pubkey
            relays=relays,
            private_key="nsec1example...",  # your private key
        )

        async def main():
            tools = await mcp_client.list_tools()
            print("Available tools:", tools)
            result = await mcp_client.call_tool("add", {"a": 1, "b": 2})
            print("1 + 2 =", result)

        asyncio.run(main())

    Full runnable script: `mcp_client.py <https://github.com/agentstr/agentstr-sdk/tree/main/examples/mcp_client.py>`_
    """
    def __init__(self, mcp_pubkey: str, nostr_client: NostrClient | None = None,
                 relays: list[str] | None = None, private_key: str | None = None, nwc_str: str | None = None):
        """Initialize the MCP client.

        Args:
            mcp_pubkey: Public key of the MCP server to interact with.
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.mcp_pubkey = get_public_key(mcp_pubkey).hex()
        self.tool_to_sats_map = {}  # Maps tool names to their satoshi costs

    async def list_tools(self) -> dict[str, Any] | None:
        """Retrieve the list of available tools from the MCP server.

        Returns:
            Dictionary of tools with their metadata, or None if not found.
        """
        metadata = await self.client.get_metadata_for_pubkey(self.mcp_pubkey)
        tools = json.loads(metadata.about)
        for tool in tools["tools"]:
            self.tool_to_sats_map[tool["name"]] = tool["satoshis"]
        return tools

    async def call_tool(self, name: str, arguments: dict[str, Any], timeout: int = 60) -> dict[str, Any] | None:
        """Call a tool on the MCP server with provided arguments.

        Args:
            name: Name of the tool to call.
            arguments: Dictionary of arguments for the tool.
            timeout: Timeout in seconds for receiving a response.

        Returns:
            Response dictionary from the server, or None if no response.
        """
        response = await self.client.send_direct_message_and_receive_response(self.mcp_pubkey, json.dumps({
            "action": "call_tool", "tool_name": name, "arguments": arguments,
        }), timeout=timeout)

        if response is None:
            logger.warning("Tool call returned None")
            return None

        message = response.message
        timestamp = int(time.time()) + 1

        logger.debug(f"MCP Client received message: {message}")
        if isinstance(message, str) and message.startswith("lnbc"):
            invoice = message.strip()
            logger.info(f"Paying invoice: {invoice}")
            await self.client.nwc_relay.try_pay_invoice(invoice=invoice, amount=self.tool_to_sats_map[name])
            response = await self.client.receive_direct_message(self.mcp_pubkey, timestamp=timestamp, timeout=timeout)

        if response:
            logger.debug(f"MCP Client received response.message: {response.message}")
            return json.loads(response.message)
        return None
