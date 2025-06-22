"""agentstr.commands
====================

Utility classes for parsing and handling *exclamation-prefixed* commands that
are commonly used by chat bots or conversational agents on Nostr.

`Commands` is a **lightweight dispatcher**: it strips the leading ``!`` from an
incoming command string, resolves the first word against a registry of
callbacks and finally awaits the selected coroutine. If the command is
unknown—or if the message does not start with an exclamation mark—the
``default`` coroutine is invoked instead (and can be customised by
sub-classes).

`DefaultCommands` is a concrete implementation that ships with the SDK. It
implements four convenience commands that are useful for the majority of
agents:

* ``!help`` – list all available commands
* ``!describe`` – show the agent's name and description
* ``!balance`` – return the user's current satoshi balance (pulled from the database)
* ``!deposit [amount]`` – create a Nostr Wallet Connect invoice so the user can top-up their balance and automatically credit it after settlement

Examples
--------

>>> cmds = DefaultCommands(db, nostr_client, agent_info)
>>> await cmds.run_command("!help", pubkey)

"""
from typing import Callable
from agentstr.database import Database
from agentstr.logger import get_logger

logger = get_logger(__name__)


class Commands:
    """Generic dispatcher that routes *exclamation-prefixed* commands to
    asynchronous handler functions.

    Parameters
    ----------
    nostr_client : NostrClient
        Client instance used to send direct messages back to users.
    commands : dict[str, Callable[[str, str], Awaitable[None]]]
        Mapping from *command name* (without the leading ``!``) to an async
        coroutine accepting ``(command_text, pubkey)``.
    """
    def __init__(self, nostr_client: 'NostrClient', commands: dict[str, Callable[[str, str], None]]):
        self.nostr_client = nostr_client
        self.commands = commands

    async def default(self, command: str, pubkey: str):
        """Fallback handler for *unknown* or *non-command* messages.

        Parameters
        ----------
        command : str
            The raw message text received from the user.
        pubkey : str
            Hex-encoded public key identifying the sender. The dispatcher will
            reply to this pubkey via a Nostr DM.
        """
        await self.nostr_client.send_direct_message(pubkey, f"Invalid command: {command}")

    async def run_command(self, command: str, pubkey: str):
        """Parse the incoming text and forward it to the matching command
        coroutine.

        The method expects an *exclamation-prefixed* string such as
        ``"!help"`` or ``"!deposit 100"``.
        """
        if not command.startswith("!"):
            await self.default(command, pubkey)
            return
        command = command[1:].strip()
        if command.split()[0] not in self.commands:
            await self.default(command, pubkey)
            return
        await self.commands[command.split()[0]](command, pubkey)


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
    agent_info : AgentCard
        Metadata about the running agent (name, description, …) used by
        ``!describe``.
    """
    def __init__(self, db: Database, nostr_client: 'NostrClient', agent_info: 'AgentCard'):
        self.db = db
        self.agent_info = agent_info
        self.nostr_client = nostr_client
        super().__init__(
            nostr_client=nostr_client,
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
        agent_info = self.agent_info
        description = "I am " + agent_info.name + "\n\nThis is my description:\n\n" + agent_info.description
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
        
        