from dotenv import load_dotenv

load_dotenv()

import os
import asyncio

from agentstr import NostrClient, PrivateKey


def private_to_public_key(private_key: str) -> str:
    return PrivateKey.from_nsec(private_key).public_key.bech32()


# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
langgraph_agent_private_key = os.getenv("EXAMPLE_LANGGRAPH_AGENT_NSEC")
agno_agent_private_key = os.getenv("EXAMPLE_AGNO_AGENT_NSEC")
dspy_agent_private_key = os.getenv("EXAMPLE_DSPY_AGENT_NSEC")
pydantic_agent_private_key = os.getenv("EXAMPLE_PYDANTIC_AGENT_NSEC")
openai_agent_private_key = os.getenv("EXAMPLE_OPENAI_AGENT_NSEC")
google_agent_private_key = os.getenv("EXAMPLE_GOOGLE_AGENT_NSEC")


async def ask_langgraph_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(langgraph_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(langgraph_agent_private_key),
        timeout=900,
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(langgraph_agent_private_key),
        timeout=900,
    )
    print(response.message)

async def ask_agno_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(agno_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(agno_agent_private_key),
        timeout=900,
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(agno_agent_private_key),
        timeout=900,
    )
    print(response.message)

async def ask_dspy_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(dspy_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(dspy_agent_private_key),
        timeout=900,
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(dspy_agent_private_key),
        timeout=900,
    )
    print(response.message)

async def ask_pydantic_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(pydantic_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)

async def ask_openai_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(openai_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)

async def ask_google_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(google_agent_private_key),
        "What's the weather in San Francisco?",
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(google_agent_private_key),
        timeout=900,
    )
    print(response.message)
    response = await client.receive_direct_message(
        private_to_public_key(google_agent_private_key),
        timeout=900,
    )
    print(response.message)

if __name__ == "__main__":
    #asyncio.run(ask_agno_agent())
    #asyncio.run(ask_dspy_agent())
    #asyncio.run(ask_google_agent())
    #asyncio.run(ask_langgraph_agent())
    asyncio.run(ask_openai_agent())
    #asyncio.run(ask_pydantic_agent())
    