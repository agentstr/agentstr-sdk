from dotenv import load_dotenv

load_dotenv()

import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agentstr import ChatInput, NostrAgentServer, NostrMCPClient
from agentstr.mcp.agno import to_agno_tools

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_AGNO_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    agno_tools = await to_agno_tools(nostr_mcp_client)

    for tool in agno_tools:
        print(f'Found {tool.name}: {tool.description}')

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
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.arun(message=input.messages[-1], session_id=input.thread_id)
        return result.content

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
