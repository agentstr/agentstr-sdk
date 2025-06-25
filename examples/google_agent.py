from dotenv import load_dotenv

load_dotenv()

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agentstr import ChatInput, NostrAgentServer, NostrMCPClient
from agentstr.mcp.google import to_google_tools

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=os.getenv("NOSTR_RELAYS").split(","),
                                  private_key=os.getenv("EXAMPLE_GOOGLE_AGENT_NSEC"),
                                  mcp_pubkey=os.getenv("EXAMPLE_MCP_SERVER_PUBKEY"),
                                  nwc_str=os.getenv("MCP_CLIENT_NWC_CONN_STR"))

async def agent_server():
    # Define tools
    google_tools = await to_google_tools(nostr_mcp_client)

    for tool in google_tools:
        print(f'Found {tool.name}: {tool.description}')

    # Define Google agent
    agent = Agent(
        name="google_agent",
        model=LiteLlm(
            model=os.getenv("LLM_MODEL_NAME"),
            api_base=os.getenv("LLM_BASE_URL").rstrip('/v1'),
            api_key=os.getenv("LLM_API_KEY")
        ),
        instruction="You are a helpful assistant.",
        tools=google_tools,
    )

    # Session and Runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name='nostr_example', session_service=session_service)

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        content = types.Content(role='user', parts=[types.Part(text=input.messages[-1])])
        await session_service.create_session(app_name='nostr_example', user_id=input.thread_id, session_id=input.thread_id)
        events_async = runner.run_async(user_id=input.thread_id,
                                        session_id=input.thread_id,
                                        new_message=content)
        async for event in events_async:
            print(f'Received event: {event}')
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("Agent Response: ", final_response)
                return final_response
        return None

    # Create Nostr Agent Server
    server = NostrAgentServer(nostr_mcp_client=nostr_mcp_client,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())