from dotenv import load_dotenv

load_dotenv()

import os

import dspy

from agentstr import NostrAgentServer, NostrMCPClient, NostrAgent, AgentCard, Skill
from agentstr.mcp.providers.dspy import to_dspy_tools
from agentstr.agents.providers.dspy import dspy_chat_generator

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_DSPY_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():    
    # Convert tools to DSPy tools
    dspy_tools = await to_dspy_tools(nostr_mcp_client)

    # Create ReAct agent
    agent = dspy.ReAct("question -> answer: str", tools=dspy_tools)

    # Configure DSPy
    dspy.configure(lm=dspy.LM(model=os.getenv("LLM_MODEL_NAME"), 
                              api_base=os.getenv("LLM_BASE_URL").rstrip("/v1"), 
                              api_key=os.getenv("LLM_API_KEY"), 
                              model_type="chat",
                              temperature=0))

    # Create chat generator
    chat_generator = dspy_chat_generator(agent, [nostr_mcp_client])

    # Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="DSPy Agent", 
            description="A helpful assistant", 
            skills=await nostr_mcp_client.get_skills(), 
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
