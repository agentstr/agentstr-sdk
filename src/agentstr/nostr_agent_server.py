import asyncio
from collections.abc import Callable
from typing import Any, Literal
import uuid
import json

from pynostr.event import Event

from agentstr.nostr_agent import NostrAgent
from agentstr.database.base import BaseDatabase
from agentstr.models import AgentCard, ChatInput, ChatOutput, Message, User, NoteFilters
from agentstr.commands import Commands, DefaultCommands
from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient
from agentstr.mcp.nostr_mcp_client import NostrMCPClient

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
                 nostr_agent: NostrAgent,
                 nostr_client: NostrClient | None = None,
                 nostr_mcp_client: NostrMCPClient | None = None,
                 relays: list[str] | None = None,
                 private_key: str | None = None,
                 nwc_str: str | None = None,
                 db: BaseDatabase | None = None,
                 note_filters: NoteFilters | None = None,
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
            db: Database instance (optional).
            note_filters: Filters for listening to Nostr notes (optional).
            price_handler: PriceHandler to use for determining if an agent can handle a request and calculate the cost (optional).
        """
        self.client = nostr_client or (nostr_mcp_client.client if nostr_mcp_client else NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str))
        self.nostr_agent = nostr_agent
        self.db = db
        if self.db and self.db.agent_name is None:
            self.db.agent_name = self.nostr_agent.agent_card.name
        self.commands = commands or DefaultCommands(db=self.db, nostr_client=self.client, agent_card=nostr_agent.agent_card)

    async def _save_input(self, chat_input: ChatInput):
        logger.debug(f"Saving input: {chat_input.model_dump_json()}")
        await self.db.add_message(
            thread_id=chat_input.thread_id, 
            user_id=chat_input.user_id, 
            role="user",
            message=chat_input.message,
            content=chat_input.message,
            kind="request",
            satoshis=0,
            extra_inputs=chat_input.extra_inputs or {},
            extra_outputs={}
        )

    async def _save_output(self, chat_output: ChatOutput):
        logger.debug(f"Saving output: {chat_output.model_dump_json()}")
        await self.db.add_message(
            thread_id=chat_output.thread_id, 
            user_id=chat_output.user_id, 
            role=chat_output.role,
            message=chat_output.message,
            content=chat_output.message,
            kind=chat_output.kind,
            satoshis=chat_output.satoshis,
            extra_inputs={},
            extra_outputs=chat_output.extra_outputs or {}
        )

    async def _handle_payment(self, user: User, satoshis: int):
        logger.info(f"Checking payment: {user.available_balance} >= {satoshis}")
        if user.available_balance >= satoshis:
            logger.info(f"Auto payment successful: {user.available_balance} >= {satoshis}")
            user.available_balance -= satoshis
            await self.db.upsert_user(user)
            return True
        logger.info(f"Auto payment failed: {user.available_balance} < {satoshis}")
        return False


    async def chat(self, chat_input: ChatInput, event: Event,delegation_tags: dict[str, str], history: list[Message]):
        """Send a message to the agent and retrieve the response.

        Args:
            chat_input: The chat input to send to the agent.

        Returns:
            Response from the agent, or an error message.
        """
        recipient_pubkey = event.pubkey

        # Paying user is always the recipient of the message
        paying_user = await self.db.get_user(user_id=recipient_pubkey)

        # Save user message to db
        await self._save_input(chat_input)
        
        # Handle base agent payments
        if self.nostr_agent.agent_card.satoshis or 0 > 0:
            if not await self._handle_payment(paying_user, self.nostr_agent.agent_card.satoshis):
                invoice = await self.client.nwc_relay.make_invoice(amount=self.nostr_agent.agent_card.satoshis or 0, description="Agenstr tool call")
                message = f"Pay {self.nostr_agent.agent_card.satoshis} sats to use this agent.\n\n{invoice}"
                await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                if not await self.client.nwc_relay.wait_for_payment_success(invoice):
                    message = "Payment failed. Please try again."
                    await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                    return

        # Handle tool payments
        async for chunk in self.nostr_agent.chat_stream(chat_input):
            try:
                # Save output
                await self._save_output(chunk)

                # Handle response kinds (payments, user input, etc.)
                if chunk.kind == "requires_payment" and (chunk.satoshis or 0) > 0:
                    logger.info(f"Tool call requires payment: {chunk}")
                    if not await self._handle_payment(paying_user, chunk.satoshis):
                        invoice = await self.client.nwc_relay.make_invoice(amount=chunk.satoshis, description="Agenstr tool call")
                        logger.info(f"Invoice: {invoice}")
                        message = f'{chunk.message}\n\nJust pay {chunk.satoshis} sats.\n\n{invoice}'
                        await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                        if await self.client.nwc_relay.wait_for_payment_success(invoice):
                            continue
                        else:
                            message = "Payment failed. Please try again."
                            await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                            break
                elif chunk.kind == 'requires_input':
                    logger.info(f"Requires input: {chunk}")
                    raise NotImplementedError("requires_input not implemented")
                elif chunk.kind == 'tool_message':
                    logger.info(f"Tool message: {chunk}")
                    continue
                else:
                    logger.info(f"Final response: {chunk}")
                    message = chunk.message
                    await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)     
                    
            except Exception as e:
                logger.error(f"Error in chat: {e}")
                message = "An error occurred. Please try again."
                await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                break

    async def _parse_message(self, event: Event, message: str) -> str | None:
        message = message.strip()
        if message.startswith("{") or message.startswith("["):
            logger.debug("Skipping JSON message")
            return None
        elif message.startswith("lnbc") and " " not in message:
            logger.debug("Ignoring lightning invoices")
            return None
        elif message.startswith("!"):
            logger.debug("Processing command: " + message)
            await self.commands.run_command(message, event.pubkey)
            return None
        elif len(message) == 0:
            logger.debug("Ignoring empty message")
            return None
        return message

    def _check_delegation(self, event: Event) -> dict[str, str] | None:
        tags = event.get_tag_dict()
        delegated_user_id, delegated_thread_id = None, None
        if "t" in tags and len(tags["t"]) > 0 and len(tags["t"][0]) > 1:
            d_user_id = tags["t"][0][0]
            delegated_user_id = f'{event.pubkey}:{d_user_id}'  # Keep delegation threads separate from direct user threads
            delegated_thread_id = tags["t"][0][1]           
        return {"t": [delegated_user_id, delegated_thread_id]} if delegated_user_id and delegated_thread_id else None

    async def _get_user_and_thread_ids(self, event: Event) -> tuple[str | None, str | None, dict[str, str] | None]:
        # Check for delegated thread
        delegation_tags = self._check_delegation(event)
        logger.debug(f"Delegation tags: {delegation_tags}")

        if delegation_tags:
            user_id = delegation_tags["t"][0][0]
            thread_id = delegation_tags["t"][0][1]
        else:
            user_id = event.pubkey
            user = await self.db.get_user(user_id=user_id)
            thread_id = user.current_thread_id or uuid.uuid4().hex

        # Set active thread
        logger.debug(f"Setting active thread for user {user_id}: {thread_id}")
        await self.db.set_current_thread_id(user_id=user_id, thread_id=thread_id)

        return user_id, thread_id, delegation_tags

    async def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        # Parse message
        message = await self._parse_message(event, message)
        if not message:
            return

        # Get user and thread IDs
        user_id, thread_id, delegation_tags = await self._get_user_and_thread_ids(event)

        # Get message history
        history = await self.db.get_messages(thread_id=thread_id, user_id=user_id)
        logger.debug(f"Message history: {history}")

        # Create chat input
        chat_input = ChatInput(
            messages=[message], 
            thread_id=thread_id, 
            user_id=user_id, 
            extra_inputs=delegation_tags or {}
        )

        # Chat with agent
        await self.chat(chat_input, event=event, delegation_tags=delegation_tags, history=history)


    async def start(self):
        """Start the agent server, updating metadata and listening for direct messages and notes."""
        logger.info(f"Updating metadata for {self.client.public_key.bech32()}")
        if self.nostr_agent.agent_card:
            await self.client.update_metadata(
                name="agent_server",
                username=self.nostr_agent.agent_card.name,
                display_name=self.nostr_agent.agent_card.name,
                about=self.nostr_agent.agent_card.model_dump_json(),
                nostr_metadata=self.nostr_agent.nostr_metadata,
            )

        # Start direct message listener
        tasks = []
        logger.info(f"Starting message listener for {self.client.public_key.bech32()}")
        tasks.append(self.client.direct_message_listener(callback=self._direct_message_callback))
        await asyncio.gather(*tasks)
