
from dotenv import load_dotenv
load_dotenv()

import os
from agentstr import NostrClient, PrivateKey

agent_pubkey = os.getenv("NOSTR_PUBKEY")

async def chat():
    client = NostrClient(private_key=PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        agent_pubkey,
        "What's 59 + 88232?",
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())
