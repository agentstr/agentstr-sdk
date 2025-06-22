"""Minimal Agentstr agent – echoes incoming messages."""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from agentstr import AgentCard, NostrAgentServer, ChatInput, ChatOutput


async def echo_agent(chat: ChatInput) -> str | ChatOutput:  # noqa: D401
    return chat.messages[-1]


async def main() -> None:
    card = AgentCard(
        name="EchoAgent",
        description="A minimal example that echoes messages back.",
        nostr_pubkey=os.getenv("AGENT_PUBKEY"),
    )
    server = NostrAgentServer(
        agent_info=card,
        agent_callable=echo_agent,
        relays=[os.getenv("RELAY_URL")], 
        private_key=os.getenv("AGENT_NSEC"),
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
