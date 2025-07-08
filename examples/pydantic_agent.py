from dotenv import load_dotenv

load_dotenv()

import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agentstr import NostrAgent, AgentCard, NostrAgentServer, NostrMCPClient
from agentstr.mcp.providers.pydantic import to_pydantic_tools
from agentstr.agents.providers.pydantic import pydantic_agent_callable

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("PYDANTIC_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    pydantic_tools = await to_pydantic_tools(nostr_mcp_client)

    # Define Pydantic agent
    agent = Agent(
        system="You are a helpful assistant.",
        model=OpenAIModel(
            os.getenv("LLM_MODEL_NAME"),
            provider=OpenAIProvider(
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY"),
            )
        ),
        tools=pydantic_tools,
    )

    # Define agent callable
    agent_callable = pydantic_agent_callable(agent)

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="Pydantic Agent", 
            description="A helpful assistant", 
            skills=await nostr_mcp_client.get_skills(), 
            satoshis=2), 
        agent_callable=agent_callable)

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              nostr_agent=nostr_agent)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
