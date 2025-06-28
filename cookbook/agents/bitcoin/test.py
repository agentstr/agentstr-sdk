from dotenv import load_dotenv

load_dotenv()

import os

from agentstr import NostrClient, PrivateKey


def private_to_public_key(private_key: str) -> str:
    return PrivateKey.from_nsec(private_key).public_key.bech32()


# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
agent_public_key = private_to_public_key(os.getenv("AGENT_PRIVATE_KEY"))


async def ask_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        agent_public_key,
        "what's the current hashrate of bitcoin?",
    )
    print(response.message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(ask_agent())
    