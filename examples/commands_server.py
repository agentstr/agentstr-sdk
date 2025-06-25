from dotenv import load_dotenv

load_dotenv()

import os
from agentstr.database import Database
from agentstr.commands import DefaultCommands
from agentstr import AgentCard, NostrClient, NostrAgentServer


relays   = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_MCP_SERVER_NSEC")
nwc_str = os.getenv("MCP_SERVER_NWC_CONN_STR")
server_public_key = os.getenv("EXAMPLE_MCP_SERVER_PUBKEY")

agent_info = AgentCard(name="TestAgent", description="Agent description.", nostr_pubkey=server_public_key)
nostr_client = NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)



async def run():
    db = Database()
    await db.async_init()

    commands = DefaultCommands(db, nostr_client=nostr_client, agent_info=agent_info)
    agent_server = NostrAgentServer(nostr_client=nostr_client, agent_info=agent_info, commands=commands)
    
    await agent_server.start()



if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
