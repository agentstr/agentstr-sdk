import asyncio
from collections.abc import Callable
from typing import Any

from pynostr.event import Event

from agentstr.database import Database
from agentstr.models import AgentCard, ChatInput, ChatOutput, PriceHandlerResponse, NoteFilters
from agentstr.a2a import PriceHandler
from agentstr.commands import Commands, DefaultCommands
from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient
from agentstr.nostr_mcp_client import NostrMCPClient

logger = get_logger(__name__)



class NostrAgentServer:
    """Server that integrates an external agent with the Nostr network.

    Handles direct messages and optional payments, routing them to an external agent.

    Examples
    --------
    Minimal server wiring an LLM agent (see full script)::

        import asyncio
        from langchain_openai import ChatOpenAI
        from agentstr import NostrAgentServer, NostrMCPClient, ChatInput

        relays = ["wss://relay.damus.io"]
        mcp_client = NostrMCPClient(
            mcp_pubkey="npub1example...",
            relays=relays,
            private_key="nsec1example...",
        )

        llm = ChatOpenAI(model_name="gpt-3.5-turbo")

        async def agent_callable(input: ChatInput) -> ChatOutput:
            result = await llm.ainvoke(
                {"messages": [{"role": "user", "content": input.messages[-1]}]},
            )
            return ChatOutput(message=result["messages"][-1].content)

        server = NostrAgentServer(
            nostr_mcp_client=mcp_client,
            agent_callable=agent_callable,
        )

        asyncio.run(server.start())

    Full runnable example: `nostr_langgraph_agent.py <https://github.com/agentstr/agentstr-sdk/tree/main/examples/nostr_langgraph_agent.py>`_
    """
    def __init__(self,
                 nostr_client: NostrClient | None = None,
                 nostr_mcp_client: NostrMCPClient | None = None,
                 relays: list[str] | None = None,
                 private_key: str | None = None,
                 nwc_str: str | None = None,
                 agent_info: AgentCard | None = None,
                 agent_callable: Callable[[ChatInput], str | ChatOutput] | None = None,
                 note_filters: NoteFilters | None = None,
                 price_handler: PriceHandler | None = None,
                 commands: Commands | None = None):
        """Initialize the agent server.

        Args:
            nostr_client: Existing NostrClient instance (optional).
            nostr_mcp_client: Existing NostrMCPClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            agent_info: Agent information (optional).
            agent_callable: Callable to handle agent responses.
            note_filters: Filters for listening to Nostr notes (optional).
            price_handler: PriceHandler to use for determining if an agent can handle a request and calculate the cost (optional).
        """
        self.client = nostr_client or (nostr_mcp_client.client if nostr_mcp_client else NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str))
        self.agent_info = agent_info
        self.agent_callable = agent_callable
        self.note_filters = note_filters
        self.price_handler = price_handler
        self.commands = commands or DefaultCommands(db=Database(), nostr_client=self.client, agent_info=agent_info)

    async def chat(self, message: str, thread_id: str | None = None) -> str | ChatOutput:
        """Send a message to the agent and retrieve the response.

        Args:
            message: The message to send to the agent.
            thread_id: Optional thread ID for conversation context.

        Returns:
            Response from the agent, or an error message.
        """
        return await self.agent_callable(ChatInput(messages=[message], thread_id=thread_id))

    async def _handle_paid_invoice(self, event: Event, message: str, invoice: str, price_handler_response: PriceHandlerResponse = None):
        """Handle a paid invoice."""
        if price_handler_response:
            skills_used = ", ".join(price_handler_response.skills_used)
            message = f"""I'd like to follow up on our previous exchange:

Your Request:
{message}

Your Response:
{price_handler_response.user_message}

Could you please proceed with the next steps or provide an update on this matter?

Only use the following tools: [{skills_used}]
"""

        logger.info("Handling paid invoice")

        async def on_success():
            logger.info(f"Payment succeeded for {self.agent_info.name}")
            result = await self.chat(message, thread_id=event.pubkey)
            response = str(result)
            logger.debug(f"On success response: {response}")
            await self.client.send_direct_message(event.pubkey, response)

        async def on_failure():
            response = "Payment failed. Please try again."
            logger.error(f"On failure response: {response}")
            await self.client.send_direct_message(event.pubkey, response)

        await self.client.nwc_relay.on_payment_success(
            invoice=invoice,
            callback=on_success,
            timeout=900,
            unsuccess_callback=on_failure,
        )


    async def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        if message.strip().startswith("{") or message.strip().startswith("["):
            logger.debug("Ignoring JSON messages")
            return
        elif message.strip().startswith("lnbc") and " " not in message.strip():
            logger.debug("Ignoring lightning invoices")
            return
        elif message.strip().startswith("!"):
            logger.debug("Processing command: " + message.strip())
            await self.commands.run_command(message.strip(), event.pubkey)
            return
        message = message.strip()
        invoice = None
        price_handler_response = None
        logger.debug(f"Agent request: {message}")
        try:
            response = None
            cost_sats = None
            if self.price_handler:
                price_handler_response = await self.price_handler.handle(message, self.agent_info, thread_id=event.pubkey)
                response = price_handler_response.user_message
                if price_handler_response.can_handle:
                    cost_sats = price_handler_response.cost_sats
                else:
                    await self.client.send_direct_message(event.pubkey, response)
                    return

            cost_sats = cost_sats or ((self.agent_info.satoshis or 0) if self.agent_info else 0)
            if cost_sats > 0:
                invoice = await self.client.nwc_relay.make_invoice(amount=cost_sats, description=f"Payment for {self.agent_info.name}")
                if response is not None:
                    response = f"{response}\n\nPlease pay {cost_sats} sats: {invoice}"
                else:
                    response = invoice
            else:
                result = await self.chat(message, thread_id=event.pubkey)
                response = str(result)
        except Exception as e:
            response = f"Error in direct message callback: {e}"

        logger.debug(f"Agent response: {response}")
        tasks = []
        tasks.append(self.client.send_direct_message(event.pubkey, response))
        if invoice:
            tasks.append(self._handle_paid_invoice(event, message, invoice, price_handler_response))
        await asyncio.gather(*tasks)


    async def _note_callback(self, event: Event):
        """Handle incoming notes that match the filters.

        Args:
            event: The Nostr event containing the note.
        """
        if not self.price_handler:
            logger.warning("No price handler provided. Skipping note callback.")
            return
        try:
            content = event.content
            logger.info(f"Received note from {event.pubkey}: {content}")

            price_handler_response = await self.price_handler.handle(content, self.agent_info, thread_id=event.pubkey)
            logger.info(f"Price handler response: {price_handler_response.model_dump()}")

            if price_handler_response.can_handle:
                # Formulate and send direct message to the user
                response = price_handler_response.user_message
                tasks = []
                if price_handler_response.cost_sats > 0:
                    invoice = await self.client.nwc_relay.make_invoice(amount=price_handler_response.cost_sats, description=f"Payment to {self.agent_info.name}")
                    response = f"{response}\n\nPlease pay {price_handler_response.cost_sats} sats: {invoice}"
                    tasks.append(self._handle_paid_invoice(event, content, invoice, price_handler_response))

                tasks.append(self.client.send_direct_message(event.pubkey, response))
                await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"Error processing note: {e}", exc_info=True)

    async def start(self):
        """Start the agent server, updating metadata and listening for direct messages and notes."""
        logger.info(f"Updating metadata for {self.client.public_key.bech32()}")
        if self.agent_info:
            await self.client.update_metadata(
                name="agent_server",
                display_name=self.agent_info.name,
                about=self.agent_info.model_dump_json(),
            )

        tasks = []
        # Start note listener if filters are provided (in new thread)
        if self.note_filters is not None:
            logger.info(f"Starting note listener with filters: {self.note_filters.model_dump()}")
            tasks.append(
                self.client.note_listener(
                    callback=self._note_callback,
                    pubkeys=self.note_filters.nostr_pubkeys,
                    tags=self.note_filters.nostr_tags,
                    following_only=self.note_filters.following_only,
                ),
            )

        # Start direct message listener
        logger.info(f"Starting message listener for {self.client.public_key.bech32()}")
        tasks.append(self.client.direct_message_listener(callback=self._direct_message_callback))
        await asyncio.gather(*tasks)
