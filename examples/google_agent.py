from dotenv import load_dotenv

load_dotenv()

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentstr import NostrAgent, AgentCard, NostrAgentServer, NostrMCPClient
from agentstr.mcp.providers.google import to_google_tools
from agentstr.agents.providers.google import google_agent_callable, google_chat_generator

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("GOOGLE_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
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
    #agent_callable = google_agent_callable(agent)
    chat_generator = google_chat_generator(agent, [nostr_mcp_client])

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="Google Agent", 
            description="A helpful assistant", 
            skills=await nostr_mcp_client.get_skills(), 
            satoshis=2), 
        chat_generator=chat_generator)
        #agent_callable=agent_callable)

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              nostr_agent=nostr_agent)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())