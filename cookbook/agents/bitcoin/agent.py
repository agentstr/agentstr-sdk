from dotenv import load_dotenv
from langchain_core.tools import BaseTool

load_dotenv()

import os
import uuid
import asyncio
from agentstr.nostr_agent_server import NoteFilters
from pynostr.key import PrivateKey
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from agentstr import NostrClient, NostrAgentServer, AgentCard, NostrMCPClient, Skill, ChatInput
from agentstr.mcp.langgraph import to_langgraph_tools
from langchain_openai import ChatOpenAI

# Get the environment variables
relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('AGENT_PRIVATE_KEY')

# Define LLM
model = ChatOpenAI(temperature=0,
                   base_url=os.getenv('LLM_BASE_URL'),
                   api_key=os.getenv('LLM_API_KEY'),
                   model_name=os.getenv('LLM_MODEL_NAME'))

# Initialize Nostr client
nostr_client = NostrClient(relays, private_key)

async def run():
    # Discover MCP servers
    mcp_pubkey = 'npub1m7kklaydljpjscl37xpdgtzfs66u70t5aex68pgdnsmjcx0vllrsmxl6vk'

    # Get tools from MCP servers
    tools: list[BaseTool] = await to_langgraph_tools(NostrMCPClient(
        nostr_client=nostr_client,
        mcp_pubkey=mcp_pubkey,
    ))

    # Create ReAct agent
    agent = create_react_agent(model, tools, checkpointer=MemorySaver())

    # Define skills
    skills = [Skill(
        name=tool.name,
        description=tool.description,
        satoshis=tool.metadata.get("satoshis", 0),
    ) for tool in tools]

    # Define agent info
    agent_info = AgentCard(
        name='Bitcoin Agent',
        description='This agent can query bitcoin blockchain data',
        skills=skills,
        satoshis=0,
        nostr_pubkey=PrivateKey.from_nsec(private_key).public_key.bech32(),
        nostr_relays=relays,
    )

    # Define note filters (only listen to me for now)
    note_filters = NoteFilters(
        nostr_pubkeys=['npub1jch03stp0x3fy6ykv5df2fnhtaq4xqvqlmpjdu68raaqcntca5tqahld7a'],
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        config = {"configurable": {"thread_id": input.thread_id or str(uuid.uuid4())}}
        result = await agent.ainvoke({"messages": input.messages[-1]}, config=config)
        return result["messages"][-1].content

    # Create server
    server = NostrAgentServer(nostr_client,
                              note_filters=note_filters,
                              agent_info=agent_info,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    