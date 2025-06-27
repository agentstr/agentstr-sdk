from typing import AsyncGenerator, Callable
from dotenv import load_dotenv

load_dotenv()

import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agentstr.mcp.providers.agno import to_agno_tools
from agentstr import NostrAgent, AgentCard, Skill, ChatOutput, ChatInput, NostrAgentServer, NostrMCPClient

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_AGNO_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    agno_tools = await to_agno_tools(nostr_mcp_client)

    # Define Agno agent
    agent = Agent(
        model=OpenAIChat(
            temperature=0,
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY"),
            id=os.getenv("LLM_MODEL_NAME"),
        ),
        tools=agno_tools,
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> ChatOutput | str:
        return (await agent.arun(
            message=input.message,
            session_id=input.thread_id,
            user_id=input.user_id,
        )).content

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="Agno Agent", 
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
