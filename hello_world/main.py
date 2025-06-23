"""Minimal Agentstr agent - says hello to users."""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from agentstr import AgentCard, NostrAgentServer, ChatInput, ChatOutput


async def hello_world_agent(chat: ChatInput) -> str | ChatOutput:  # noqa: D401
    return f"Hello {chat.user_id}!"


async def main() -> None:
    card = AgentCard(
        name="HelloWorldAgent",
        description="A minimal example that greets users.",
        nostr_pubkey=os.getenv("AGENT_PUBKEY"),
    )
    server = NostrAgentServer(
        agent_info=card,
        agent_callable=hello_world_agent,
        relays=[os.getenv("RELAY_URL")], 
        private_key=os.getenv("AGENT_NSEC"),
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
