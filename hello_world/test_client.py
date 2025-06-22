
from dotenv import load_dotenv
load_dotenv()

import os
from agentstr import NostrClient, PrivateKey

# Get the environment variables
relays = [os.getenv("RELAY_URL")]
agent_pubkey = os.getenv("AGENT_PUBKEY")


async def chat():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        agent_pubkey,
        "Hello, how are you?",
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())
