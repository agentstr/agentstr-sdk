from dotenv import load_dotenv

load_dotenv()

import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agentstr import NostrAgentServer, NostrMCPClient, NostrAgent, AgentCard, Skill
from agentstr.mcp.providers.langgraph import to_langgraph_tools
from agentstr.agents.providers.langgraph import langgraph_chat_generator

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_LANGGRAPH_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Convert tools to LangGraph tools
    langgraph_tools = await to_langgraph_tools(nostr_mcp_client)

    # Create react agent
    agent = create_react_agent(
        model=ChatOpenAI(temperature=0,
                         base_url=os.getenv("LLM_BASE_URL"),
                         api_key=os.getenv("LLM_API_KEY"),
                         model_name=os.getenv("LLM_MODEL_NAME")),
        tools=langgraph_tools,
        prompt="You are a helpful assistant",
    )

    # Create chat generator
    chat_generator = langgraph_chat_generator(agent, [nostr_mcp_client])

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="LangGraph Agent", 
            description="A helpful assistant", 
            skills=[Skill(name=tool.name, description=tool.description) for tool in langgraph_tools], 
            satoshis=2), 
        chat_generator=chat_generator)

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              nostr_agent=nostr_agent)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
