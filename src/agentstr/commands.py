from typing import Callable
from agentstr.database import Database


class Commands:
    def __init__(self, nostr_client: 'NostrClient', commands: dict[str, Callable[[str, str], None]]):
        self.nostr_client = nostr_client
        self.commands = commands

    async def default(self, command: str, pubkey: str):
        await self.nostr_client.send_direct_message(pubkey, f"Invalid command: {command}")

    async def run_command(self, command: str, pubkey: str):
        if not command.startswith("!"):
            await self.default(command, pubkey)
            return
        command = command[1:].strip()
        if command.split()[0] not in self.commands:
            await self.default(command, pubkey)
            return
        await self.commands[command.split()[0]](command, pubkey)


class DefaultCommands(Commands):
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
        await self.nostr_client.send_direct_message(pubkey, """Available commands:
!help - Show this help message
!balance - Show your balance
!deposit [amount] - Deposit sats to your balance""")

    async def _describe(self, command: str, pubkey: str):
        agent_info = self.agent_info
        description = "I am " + agent_info.name + "\n\nThis is my description:\n\n" + agent_info.description
        await self.nostr_client.send_direct_message(pubkey, description)

    async def _balance(self, command: str, pubkey: str):
        user = await self.db.get_user(pubkey)
        await self.nostr_client.send_direct_message(pubkey, f"Your balance is {user.available_balance} sats")

    async def _deposit(self, command: str, pubkey: str):
        if not self.nostr_client.nwc_relay:
            await self.nostr_client.send_direct_message(pubkey, "Nostr Wallet Connect (NWC) is not configured")
            return

        amount = None
        if " " in command:
            try:
                amount = int(command.split()[1])
            except ValueError:
                pass
        invoice = await self.nostr_client.nwc_relay.make_invoice(amount=amount, description="Deposit to your balance")

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
        
        