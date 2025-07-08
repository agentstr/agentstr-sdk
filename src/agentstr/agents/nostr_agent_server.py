import asyncio
from collections.abc import Callable
from typing import Any, Literal
import uuid
import json
import time

from pynostr.event import Event

from agentstr.agents.nostr_agent import NostrAgent
from agentstr.database import Database, BaseDatabase
from agentstr.models import AgentCard, ChatInput, ChatOutput, Message, User, NoteFilters
from agentstr.commands.base import Commands
from agentstr.commands.commands import DefaultCommands
from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient
from agentstr.mcp.nostr_mcp_client import NostrMCPClient

logger = get_logger(__name__)


class NostrAgentServer:
    """
    Server that exposes an agent as a Nostr-compatible chat endpoint with payment and delegation support.

    The NostrAgentServer handles:
      - Receiving and parsing direct messages and delegated messages from Nostr clients
      - Routing messages to an underlying agent (streaming or callable)
      - Managing payments for agent and tool calls via Nostr Wallet Connect (NWC)
      - Handling user and thread state, including delegated threads
      - Persisting chat history via a database
      - Sending responses, tool messages, and payment requests back to users

    Supports both streaming and non-streaming agent interfaces, and can require payment for agent or tool usage.
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
        """
        Initialize a NostrAgentServer.

        Args:
            nostr_agent (NostrAgent): The agent interface to expose over Nostr.
            nostr_client (NostrClient, optional): Pre-initialized Nostr client. If not provided, will be constructed from relays/private_key.
            nostr_mcp_client (NostrMCPClient, optional): MCP client for tool calls. Used to extract client if nostr_client not provided.
            relays (list[str], optional): List of relay URLs to connect to if no client provided.
            private_key (str, optional): Nostr private key (nsec format) for signing events and payments.
            nwc_str (str, optional): Nostr Wallet Connect string for enabling payment support.
            db (BaseDatabase, optional): Database for persisting messages and user state.
            note_filters (NoteFilters, optional): Filters for subscribing to specific Nostr notes/events.
            commands (Commands, optional): Custom command handler. If not provided, uses DefaultCommands.
        """
        self.client = nostr_client or (nostr_mcp_client.client if nostr_mcp_client else NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str))
        self.nostr_agent = nostr_agent
        self.db = db or Database()
        if self.db and self.db.agent_name is None:
            self.db.agent_name = self.nostr_agent.agent_card.name
        if self.nostr_agent.agent_card.nostr_pubkey is None:
            self.nostr_agent.agent_card.nostr_pubkey = self.client.private_key.public_key.bech32()
        if self.nostr_agent.agent_card.nostr_relays is None:
            self.nostr_agent.agent_card.nostr_relays = self.client.relays
        self.commands = commands or DefaultCommands(db=self.db, nostr_client=self.client, agent_card=nostr_agent.agent_card)

    async def _save_input(self, chat_input: ChatInput):
        """
        Persist an incoming user chat input to the database.

        Args:
            chat_input (ChatInput): The input message and metadata from the user.
        """
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
        """
        Persist an outgoing agent/tool chat output to the database.

        Args:
            chat_output (ChatOutput): The agent or tool's output message and metadata.
        """
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

    async def _check_balance_and_deduct(self, user: User, satoshis: int):
        """
        Attempt to deduct the required satoshis from the user's balance for a request.

        Args:
            user (User): The user making the request.
            satoshis (int): The required payment amount.

        Returns:
            bool: True if payment was successful or not required, False if insufficient balance.
        """
        logger.info(f"Checking payment: {user.available_balance} >= {satoshis}")
        if user.available_balance >= satoshis:
            logger.info(f"Auto payment successful: {user.available_balance} >= {satoshis}")
            user.available_balance -= satoshis
            await self.db.upsert_user(user)
            return True
        logger.info(f"Auto payment failed: {user.available_balance} < {satoshis}")
        return False

    async def _wait_for_payment(self, user: User, satoshis: int, invoice: str, timeout: int = 900, interval: int = 2):
        """
        Wait for payment to be made for a request or a deposit added to the user's balance.

        Args:
            user (User): The user making the request.
            satoshis (int): The required payment amount.
            invoice (str): The BOLT11 invoice to listen for.
            timeout (int, optional): Maximum time to wait in seconds (default: 900).
            interval (int, optional): Time between checks in seconds (default: 2).

        Returns:
            bool: True if payment was successful, False if payment failed.
        """
        logger.info(f"Waiting for payment: {user.available_balance} >= {satoshis} (timeout: {timeout}, interval: {interval})")
        start_time = time.time()
        success = False
        while True:
            if await self.client.nwc_relay.did_payment_succeed(invoice):
                logger.info(f"Payment succeeded: {invoice}")
                success = True
                break
            if self._check_balance_and_deduct(user, satoshis):
                logger.info(f"Payment succeeded from deposit.")
                success = True
                break
            if time.time() - start_time > timeout:
                logger.info(f"Payment failed: {invoice}")
                break
            await asyncio.sleep(interval)
        if not success:
            return False
        return True

    async def chat(self, chat_input: ChatInput, event: Event, delegation_tags: dict[str, str], history: list[Message]):
        """
        Send a message to the agent and stream responses, handling payments and tool calls.

        Args:
            chat_input (ChatInput): The user's message and context.
            event (Event): The original Nostr event from the user.
            delegation_tags (dict[str, str]): Delegation tags for thread/user context (if present).
            history (list[Message]): Message history for the thread/user.

        Yields:
            Streams agent/tool responses, sending each to the user and handling payment/tool logic.
        """
        recipient_pubkey = event.pubkey

        # Paying user is always the recipient of the message
        paying_user = await self.db.get_user(user_id=recipient_pubkey)

        # Save user message to db
        logger.info(f"Saving input: {chat_input.model_dump_json()}")
        await self._save_input(chat_input)
        
        # Handle base agent payments
        if self.nostr_agent.agent_card.satoshis or 0 > 0:
            logger.info(f"Checking payment: {paying_user.available_balance} >= {self.nostr_agent.agent_card.satoshis}")
            if not await self._check_balance_and_deduct(paying_user, self.nostr_agent.agent_card.satoshis):
                logger.info(f"Auto payment failed: {paying_user.available_balance} < {self.nostr_agent.agent_card.satoshis}")
                invoice = await self.client.nwc_relay.make_invoice(amount=self.nostr_agent.agent_card.satoshis or 0, description="Agenstr tool call")
                logger.info(f"Invoice: {invoice}")
                message = f"Pay {self.nostr_agent.agent_card.satoshis} sats to use this agent.\n\n{invoice}"
                await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                if not await self._wait_for_payment(paying_user, self.nostr_agent.agent_card.satoshis, invoice):
                    logger.info(f"Payment failed: {invoice}")
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
                    if not await self._check_balance_and_deduct(paying_user, chunk.satoshis):
                        logger.info(f"Auto-payment failed: {chunk}")
                        invoice = await self.client.nwc_relay.make_invoice(amount=chunk.satoshis, description="Agenstr tool call")
                        logger.info(f"Invoice: {invoice}")
                        message = f'{chunk.message}\n\nJust pay {chunk.satoshis} sats.\n\n{invoice}'
                        await self.client.send_direct_message(recipient_pubkey, message, tags=delegation_tags)
                        if await self._wait_for_payment(paying_user, chunk.satoshis, invoice):
                            logger.info(f"Payment succeeded: {invoice}")
                            continue
                        else:
                            logger.info(f"Payment failed: {invoice}")
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

    async def _parse_message(self, event: Event, message: str) -> str | ChatInput | None:
        """
        Parse and preprocess an incoming message, handling commands and filtering noise.

        Args:
            event (Event): The Nostr event containing the message.
            message (str): The raw message content.

        Returns:
            str | None: The cleaned message, or None if it should be ignored/handled elsewhere.
        """
        message = message.strip()
        if message.startswith("{") or message.startswith("["):
            logger.debug("Skipping JSON message")
            # Check if it's a valid ChatInput
            try:
                logger.debug("Checking for ChatInput")
                chat_input = ChatInput.model_validate_json(message)
                logger.debug("Valid ChatInput")
                return chat_input
            except Exception as e:
                logger.debug("Invalid ChatInput: " + str(e))
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
        """
        Check for delegation tags in a Nostr event to determine delegated user/thread context.

        Args:
            event (Event): The incoming Nostr event.

        Returns:
            dict[str, str] | None: Delegation tag mapping, or None if not delegated.
        """
        tags = event.get_tag_dict()
        delegated_user_id, delegated_thread_id = None, None
        if "t" in tags and len(tags["t"]) > 0 and len(tags["t"][0]) > 1:
            d_user_id = tags["t"][0][0]
            delegated_user_id = f'{event.pubkey}:{d_user_id}'  # Keep delegation threads separate from direct user threads
            delegated_thread_id = tags["t"][0][1]           
        return {"t": [delegated_user_id, delegated_thread_id]} if delegated_user_id and delegated_thread_id else None

    async def _get_user_and_thread_ids(self, event: Event) -> tuple[str | None, str | None, dict[str, str] | None]:
        """
        Resolve the user and thread IDs for a given event, handling delegation if present.

        Args:
            event (Event): The incoming Nostr event.

        Returns:
            tuple: (user_id, thread_id, delegation_tags)
        """
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
        """
        Callback for direct messages: parses, resolves context, and triggers agent chat.

        Args:
            event (Event): The Nostr event containing the message.
            message (str): The message content.
        """
        # Parse message
        message = await self._parse_message(event, message)
        if not message:
            return

        if isinstance(message, ChatInput):
            logger.debug(f"Received ChatInput: {message}")
            user_id = message.user_id
            thread_id = message.thread_id
            delegation_tags = None
        else:
            user_id, thread_id, delegation_tags = await self._get_user_and_thread_ids(event)

        # Get message history
        history = await self.db.get_messages(thread_id=thread_id, user_id=user_id)
        logger.debug(f"Message history: {history}")

        # Create chat input
        chat_input = ChatInput(
            message=message, 
            thread_id=thread_id, 
            user_id=user_id, 
            extra_inputs=delegation_tags or {}
        )

        # Chat with agent
        await self.chat(chat_input, event=event, delegation_tags=delegation_tags, history=history)


    async def start(self):
        """
        Start the agent server: update metadata and begin listening for direct messages and notes.

        This will:
            - Make sure the database is initialized
            - Update the agent's Nostr metadata/profile
            - Start the direct message listener
            - Run the event loop for handling all incoming messages
        """
        # Make sure db is init
        if not self.db.conn:
            await self.db.async_init()

        # Update metadata
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
