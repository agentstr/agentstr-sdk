"""Custom Framework agent (Google ADK) - Bring your own framework."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentstr import NostrAgent, AgentCard, NostrAgentServer, NostrMCPClient
from agentstr.mcp.providers.google import to_google_tools
from agentstr.agents.providers.google import google_chat_generator

# Note: the NWC_CONN_STR environment variable is used by default for payment processing
if os.getenv("NWC_CONN_STR") is None:
    raise ValueError("NWC_CONN_STR environment variable is not set")

# Note: make sure MCP_SERVER_PUBKEY is set
if os.getenv("MCP_SERVER_PUBKEY") is None:
    raise ValueError("MCP_SERVER_PUBKEY environment variable is not set")


async def main():
    # Create Nostr MCP client
    nostr_mcp_client = NostrMCPClient(mcp_pubkey=os.getenv("MCP_SERVER_PUBKEY"))

    # Convert tools to Google ADK tools
    google_tools = await to_google_tools(nostr_mcp_client)

    # Define Google agent
    agent = Agent(
        name="google_agent",
        model=LiteLlm(
            model=os.getenv("LLM_MODEL_NAME"),
            api_base=os.getenv("LLM_BASE_URL").rstrip('/v1'),
            api_key=os.getenv("LLM_API_KEY")
        ),
        instruction="You are a helpful assistant.",
        tools=google_tools,
    )

    # Define agent callable
    chat_generator = google_chat_generator(agent, [nostr_mcp_client])

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="Google Agent", 
            description="A helpful assistant", 
            skills=await nostr_mcp_client.get_skills(), 
            satoshis=0,
        ), 
        chat_generator=chat_generator
    )

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              nostr_agent=nostr_agent)

    # Start server
    await server.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
