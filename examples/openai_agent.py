from dotenv import load_dotenv

load_dotenv()

import os

from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from agentstr import ChatInput, NostrAgentServer, NostrMCPClient
from agentstr.mcp.openai import to_openai_tools

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_OPENAI_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    openai_tools = await to_openai_tools(nostr_mcp_client)

    for tool in openai_tools:
        print(f'Found {tool.name}: {tool.description}')

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
    async def agent_callable(input: ChatInput) -> str:
        result = await Runner.run(agent, input=input.messages[-1])
        return result.final_output

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())