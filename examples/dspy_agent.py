from dotenv import load_dotenv

load_dotenv()

import os

import dspy

from agentstr import NostrAgentServer, NostrMCPClient, ChatInput
from agentstr.mcp.dspy import to_dspy_tools

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_DSPY_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():    
    # Convert tools to DSPy tools
    dspy_tools = await to_dspy_tools(nostr_mcp_client)

    for tool in dspy_tools:
        print(f'Found {tool.name}: {tool.desc}')

    # Create ReAct agent
    react = dspy.ReAct("question -> answer: str", tools=dspy_tools)

    # Configure DSPy
    dspy.configure(lm=dspy.LM(model=os.getenv("LLM_MODEL_NAME"), 
                              api_base=os.getenv("LLM_BASE_URL").rstrip("/v1"), 
                              api_key=os.getenv("LLM_API_KEY"), 
                              model_type="chat",
                              temperature=0))

    # Define agent callable
    async def agent_callable(chat_input: ChatInput) -> str:
        return (await react.acall(question=chat_input.messages[-1])).answer

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
