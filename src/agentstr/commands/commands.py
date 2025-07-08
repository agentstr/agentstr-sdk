"""
Example Usage
-------------

>>> cmds = DefaultCommands(db, nostr_client, agent_card)
>>> await cmds.run_command("!help", pubkey)

"""
from typing import Callable
from agentstr.database import BaseDatabase, Database
from agentstr.commands.base import Commands
from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient
from agentstr.models import AgentCard


logger = get_logger(__name__)


class DefaultCommands(Commands):
    """Opinionated default command set that most Agentstr agents will want to
    expose.

    Besides inheriting all behaviour from :class:`Commands`, this class wires
    up four pre-defined commands (``help``, ``describe``, ``balance`` and
    ``deposit``) and provides the concrete handler implementations.

    Parameters
    ----------
    db : Database
        Persistent storage used for reading/updating a user's balance.
    nostr_client : NostrClient
        Active client connection for sending replies and NWC invoices.
    agent_card : AgentCard
        Metadata about the running agent (name, description, …) used by
        ``!describe``.
    """
    def __init__(self, db: BaseDatabase | None = None, nostr_client: 'NostrClient | None' = None, agent_card: AgentCard | None = None):
        self.db = db or Database()
        self.agent_card = agent_card
        self.nostr_client = nostr_client or NostrClient()
        super().__init__(
            nostr_client=self.nostr_client,
            commands={
                "help": self._help,
                "describe": self._describe,
                "balance": self._balance,
                "deposit": self._deposit,
            }
        )
    
    async def _help(self, command: str, pubkey: str):
        """Return a short overview of all built-in commands."""
        await self.nostr_client.send_direct_message(pubkey, """Available commands:
!help - Show this help message
!describe - Show the agent's name and description
!balance - Show your balance
!deposit [amount] - Deposit sats to your balance""")

    async def _describe(self, command: str, pubkey: str):
        """Send the agent's name and description back to the user."""
        agent_card = self.agent_card
        if agent_card is None:
            description = "No agent card found"
        else:
            description = "I am " + agent_card.name + "\n\nThis is my description:\n\n" + agent_card.description
        await self.nostr_client.send_direct_message(pubkey, description)

    async def _balance(self, command: str, pubkey: str):
        """Look up and return the caller's current satoshi balance."""
        user = await self.db.get_user(pubkey)
        await self.nostr_client.send_direct_message(pubkey, f"Your balance is {user.available_balance} sats")

    async def _deposit(self, command: str, pubkey: str):
        """Create a NWC invoice and credit the user's balance after payment.

        The user must append an *amount in sats* to the command, e.g.
        ``"!deposit 1000"``.
        """
        if not self.nostr_client.nwc_str:
            await self.nostr_client.send_direct_message(pubkey, "Nostr Wallet Connect (NWC) is not configured")
            return

        amount = None
        if " " in command:
            try:
                amount = int(command.split()[1])
            except ValueError:
                pass

        if not amount:
            await self.nostr_client.send_direct_message(pubkey, "Please specify an amount in sats")
            return

        logger.info(f"Creating invoice for {amount} sats")
        invoice = await self.nostr_client.nwc_relay.make_invoice(amount=amount, description="Deposit to your balance")
        logger.info(f"Invoice created: {invoice}")

        if not invoice:
            await self.nostr_client.send_direct_message(pubkey, "Failed to create invoice")
            return

        await self.nostr_client.send_direct_message(pubkey, invoice)

        async def on_payment_success():
            user = await self.db.get_user(pubkey)
            user.available_balance += amount
            await self.db.upsert_user(user)
            await self.nostr_client.send_direct_message(pubkey, f"Payment successful! Your new balance is {user.available_balance} sats")
        
        async def on_payment_failure():
            await self.nostr_client.send_direct_message(pubkey, "Payment failed. Please try again.")
        
        await self.nostr_client.nwc_relay.on_payment_success(
            invoice=invoice,
            callback=on_payment_success,
            timeout=900,
            unsuccess_callback=on_payment_failure,
        )
        
        