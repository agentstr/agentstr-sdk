from typing import Callable

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
