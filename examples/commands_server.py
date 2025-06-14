from dotenv import load_dotenv

load_dotenv()

import os
from agentstr.database import Database
from agentstr.commands import DefaultCommands
from agentstr.nostr_agent_server import NostrAgentServer
from agentstr import AgentCard, NostrClient


relays   = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_MCP_SERVER_NSEC")


agent_info = AgentCard(name="TestAgent", description="Agent description.", nostr_pubkey="npub1pml2vm255v2e23rces5j2967e4t7g3jgm43hmysvjr8frttxyphqznpr36")
nostr_client = NostrClient(relays=relays, private_key=private_key)



async def run():
    db = Database()
    await db.async_init()

    commands = DefaultCommands(db, nostr_client=nostr_client, agent_info=agent_info)
    agent_server = NostrAgentServer(nostr_client=nostr_client, agent_info=agent_info, commands=commands)
    
    await agent_server.start()



if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
