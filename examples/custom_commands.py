from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from agentstr import AgentstrAgent, NostrClient, PrivateKey
from agentstr.commands import DefaultCommands


# Override DefaultCommands to add a custom command
class CustomCommands(DefaultCommands):
    def __init__(self):
        super().__init__()
        self.commands.update({
            "custom": self._custom,
        })
        print(f'Commands: {self.commands}')
    
    # Custom command handler (invoked when user sends "!custom")
    async def _custom(self, command: str, pubkey: str):
        await self.nostr_client.send_direct_message(pubkey, "Custom command received!")


# Run the agent
async def server():
    # Create the agent with custom commands
    agent = AgentstrAgent(
        name="Custom Commands",
        description="Agent with custom commands",
        commands=CustomCommands()
    )
    await agent.start()


# Run the client
async def client():
    # Wait for startup
    await asyncio.sleep(5)

    # Send custom command
    client = NostrClient(private_key=PrivateKey().bech32())
    await client.send_direct_message(os.getenv("NOSTR_PUBKEY"), "!help")
    await client.send_direct_message(os.getenv("NOSTR_PUBKEY"), "!custom")
    

# Main function
async def main():
    await asyncio.gather(server(), client())


if __name__ == "__main__":
    asyncio.run(main())
    