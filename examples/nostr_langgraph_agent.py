from dotenv import load_dotenv

load_dotenv()

import os
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agentstr import NostrAgentServer, NostrMCPClient, ChatInput, Database, ChatOutput, NostrAgent, AgentCard, Skill
from agentstr.mcp.providers.langgraph import to_langgraph_tools

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_LANGGRAPH_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Convert tools to LangGraph tools
    langgraph_tools = await to_langgraph_tools(nostr_mcp_client)

    for tool in langgraph_tools:
        print(f'Found {tool.name}: {tool.description}')

    # Create react agent
    agent = create_react_agent(
        model=ChatOpenAI(temperature=0,
                         base_url=os.getenv("LLM_BASE_URL"),
                         api_key=os.getenv("LLM_API_KEY"),
                         model_name=os.getenv("LLM_MODEL_NAME")),
        tools=langgraph_tools,
        prompt="You are a helpful assistant",
    )

    # Define agent callable
    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        async for chunk in agent.astream(
            {"messages": [{"role": "user", "content": input.messages[-1]}]},
            stream_mode="updates"
        ):
            print(f'Chunk: {chunk}')
            if 'agent' in chunk:
                update = chunk['agent']['messages'][-1]
                if update.tool_calls:
                    print(f'Tool calls: {update.tool_calls}')
                    total_satoshis = 0
                    for tool_call in update.tool_calls:
                        satoshis = nostr_mcp_client.tool_to_sats_map.get(tool_call['name'], 0)
                        total_satoshis += satoshis
                    print(f'Total satoshis: {total_satoshis}')
                    yield ChatOutput(
                        message=update.content,
                        thread_id=input.thread_id,
                        kind="requires_payment",
                        user_id=input.user_id,
                        satoshis=total_satoshis
                    )
                else:
                    yield ChatOutput(
                        message=update.content,
                        thread_id=input.thread_id,
                        kind="final_response",
                        user_id=input.user_id
                    )
            elif 'tools' in chunk:
                for message in chunk['tools']['messages']:
                    yield ChatOutput(
                        message=message.content,
                        thread_id=input.thread_id,
                        kind="tool_message",
                        user_id=input.user_id,
                        role="tool"
                    )

    nostr_agent = NostrAgent(
        agent_card=AgentCard(
            name="LangGraph Agent", 
            description="A helpful assistant", 
            skills=[Skill(name=tool.name, description=tool.description) for tool in langgraph_tools], 
            nostr_pubkey=nostr_mcp_client.client.private_key.public_key.bech32(), 
            nostr_relays=nostr_mcp_client.client.relays,
            satoshis=2), 
        chat_generator=chat_generator)

    db = Database()
    await db.async_init()   

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              nostr_agent=nostr_agent,
                              db=db)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
