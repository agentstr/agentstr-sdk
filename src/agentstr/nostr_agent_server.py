import asyncio
from collections.abc import Callable
from typing import Any, Literal
import uuid
import json

from pynostr.event import Event

from agentstr.nostr_agent import NostrAgent
from agentstr.database.base import BaseDatabase
from agentstr.models import AgentCard, ChatInput, Message, User, NoteFilters
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

    async def chat(self, chat_input: ChatInput):
        """Send a message to the agent and retrieve the response.

        Args:
            chat_input: The chat input to send to the agent.

        Returns:
            Response from the agent, or an error message.
        """

        # Handle base agent payments
        if self.nostr_agent.agent_card.satoshis or 0 > 0:
            invoice = await self.client.nwc_relay.make_invoice(amount=self.nostr_agent.agent_card.satoshis or 0, description="Agenstr tool call")
            message = f"Pay {self.nostr_agent.agent_card.satoshis or 0} sats to use this agent.\n\n{invoice}"
            await self.client.send_direct_message(chat_input.user_id, message)
            if not await self.client.nwc_relay.wait_for_payment_success(invoice):
                message = "Payment failed. Please try again."
                await self.client.send_direct_message(chat_input.user_id, message)
                return

        # Handle tool payments
        async for chunk in self.nostr_agent.chat_stream(chat_input):
            try:
                if chunk.kind == "requires_payment" and (chunk.satoshis or 0) > 0:
                    logger.info(f"Requires payment: {chunk}")
                    invoice = await self.client.nwc_relay.make_invoice(amount=chunk.satoshis, description="Agenstr tool call")
                    logger.info(f"Invoice: {invoice}")
                    message = f'{chunk.message}\n\nJust pay {chunk.satoshis} sats.\n\n{invoice}'
                    await self.client.send_direct_message(chat_input.user_id, message)
                    if await self.client.nwc_relay.wait_for_payment_success(invoice):
                        continue
                    else:
                        message = "Payment failed. Please try again."
                        await self.client.send_direct_message(chat_input.user_id, message)
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
                    await self.client.send_direct_message(chat_input.user_id, message)     
                    
                # Handle saving Chat output
                #if chat_input.thread_id and chat_input.user_id:
                #    await self.db.add_message(thread_id=chat_input.thread_id, user_id=chat_input.user_id, role="agent", content=message)
            except Exception as e:
                logger.error(f"Error in chat: {e}")
                message = "An error occurred. Please try again."
                await self.client.send_direct_message(chat_input.user_id, message)
                break

    async def _parse_message(self, event: Event, message: str) -> str | None:
        message = message.strip()
        if message.startswith("{") or message.startswith("["):
            try:
                message_json = json.loads(message)
                if "action" in message_json and message_json["action"] == "chat":
                    logger.info(f"Received chat message from agent: {message_json}")
                    raise NotImplementedError("Chat messages are not supported yet")
            except json.JSONDecodeError:
                logger.debug(f'Unable to parse JSON message: {message}')
                return None
            logger.debug("Ignoring JSON messages")
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

    async def _handle_delegated_thread(self, event: Event) -> tuple[str | None, str | None, str | None, dict[str, str] | None, list[Message]]:
        # Check for delegated thread
        tags = event.get_tag_dict()
        delegated_user_id, delegated_thread_id = None, None
        reply_to_user_id = event.pubkey
        if "t" in tags and len(tags["t"]) > 0 and len(tags["t"][0]) > 1:
            d_user_id = tags["t"][0][0]
            delegated_user_id = f'{event.pubkey}:{d_user_id}'  # Keep delegation threads separate from direct user threads
            delegated_thread_id = tags["t"][0][1]            

        delegated_tags = {"t": [delegated_user_id, delegated_thread_id]} if delegated_user_id and delegated_thread_id else None
        logger.debug(f"Delegated tags: {delegated_tags}")

        # Get target user and thread
        db_user_id = delegated_user_id or reply_to_user_id
        db_user = await self.db.get_user(user_id=db_user_id)
        if not db_user.current_thread_id:
            logger.debug("No current thread ID found for target user, creating new thread (or delegating)")
            db_thread_id = delegated_thread_id or uuid.uuid4().hex
            await self.db.set_current_thread_id(user_id=db_user_id, thread_id=db_thread_id)
        else:
            logger.debug(f"Current thread ID found for target user: {db_user.current_thread_id}")
            db_thread_id = db_user.current_thread_id

        logger.debug(f"Target user: {db_user_id}, target thread: {db_thread_id}")
        
        # Get message history
        history = await self.db.get_messages(thread_id=db_thread_id, user_id=db_user_id)
        logger.debug(f"Message history: {history}")

        # Figure out who's paying
        if reply_to_user_id == db_user_id:
            paying_user = db_user
        else:
            paying_user = await self.db.get_user(user_id=reply_to_user_id)

        logger.debug(f"Paying user: {paying_user}")
        return db_thread_id, db_user_id, reply_to_user_id, delegated_tags, history

    async def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        message = await self._parse_message(event, message)
        if not message:
            return

        db_thread_id, db_user_id, reply_to_user_id, delegated_tags, history = await self._handle_delegated_thread(event)

        # If paying user has a sufficient balance, proceed with request
        #if db_thread_id and db_user_id:
        #    await self.db.add_message(thread_id=db_thread_id, user_id=db_user_id, role="user", content=message)

        chat_input = ChatInput(messages=[message], thread_id=db_thread_id, user_id=db_user_id, history=history)

        await self.chat(chat_input)


    async def start(self):
        """Start the agent server, updating metadata and listening for direct messages and notes."""
        logger.info(f"Updating metadata for {self.client.public_key.bech32()}")
        if self.nostr_agent.agent_card:
            await self.client.update_metadata(
                name="agent_server",
                display_name=self.nostr_agent.agent_card.name,
                about=self.nostr_agent.agent_card.model_dump_json(),
            )

        # Start direct message listener
        tasks = []
        logger.info(f"Starting message listener for {self.client.public_key.bech32()}")
        tasks.append(self.client.direct_message_listener(callback=self._direct_message_callback))
        await asyncio.gather(*tasks)
