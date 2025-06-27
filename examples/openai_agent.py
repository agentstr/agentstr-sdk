from dotenv import load_dotenv

load_dotenv()

import os

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from agentstr import NostrAgent, AgentCard, NostrAgentServer, NostrMCPClient
from agentstr.mcp.providers.openai import to_openai_tools
from agentstr.agents.providers.openai import openai_agent_callable

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_OPENAI_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    openai_tools = await to_openai_tools(nostr_mcp_client)
    
    # Define OpenAI agent
    agent = Agent(
        name="OpenAI Agent",
        instructions="You are a helpful assistant.",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("LLM_MODEL_NAME"),
            openai_client=AsyncOpenAI(
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY"),
            )
        ),
        tools=openai_tools,
    )

    # Define agent callable
    agent_callable = openai_agent_callable(agent)

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="OpenAI Agent", 
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