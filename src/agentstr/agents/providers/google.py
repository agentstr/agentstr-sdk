from typing import AsyncGenerator, Callable
from google.adk.agents import Agent
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.models import ChatInput, ChatOutput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentstr.logger import get_logger

logger = get_logger(__name__)

def google_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    """Create a callable that can be used with the Agentstr framework.
    
    Args:
        agent: The Google Agent to wrap.
    
    Returns:
        A callable that can be used with the Agentstr framework.
    """
    # Session and Runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name='agentstr', session_service=session_service)

    async def agent_callable(input: ChatInput):
        content = types.Content(role='user', parts=[types.Part(text=input.message)])
        await session_service.create_session(app_name='agentstr', user_id=input.thread_id, session_id=input.thread_id)
        events_async = runner.run_async(user_id=input.thread_id,
                                        session_id=input.thread_id,
                                        new_message=content)
        async for event in events_async:
            logger.info(f'Received event: {event}')
            if event.is_final_response():
                final_response = event.content.parts[0].text
                logger.info(f"Google agent callable response: {final_response}")
                return final_response
        return None
    return agent_callable


def google_chat_generator(agent: Agent, mcp_clients: list[NostrMCPClient] | None = None) -> Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]:
    """Create a chat generator from a Google Agent. Supports human-in-the-loop, streaming messages, and streaming payments.

    Args:
        agent: The Google Agent to wrap.
        mcp_clients: A list of NostrMCPClient objects (optional).
    
    Returns:
        An async generator that can be used with the Agentstr framework.
    """
    tool_to_sats_map = {}
    if mcp_clients is not None and len(mcp_clients) > 0:
        for mcp_client in mcp_clients:
            tool_to_sats_map.update(mcp_client.tool_to_sats_map)

    # Session and Runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name='agentstr', session_service=session_service)

    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        content = types.Content(role='user', parts=[types.Part(text=input.message)])
        await session_service.create_session(app_name='agentstr', user_id=input.thread_id, session_id=input.thread_id)
        events_async = runner.run_async(user_id=input.thread_id,
                                        session_id=input.thread_id,
                                        new_message=content)
        async for event in events_async:
            logger.info(f'Received event: {event}')
            if event.is_final_response():
                final_response = event.content.parts[0].text
                logger.info(f"Final response: {final_response}")
                yield ChatOutput(
                    message=final_response,
                    content=event.model_dump_json(),
                    thread_id=input.thread_id,
                    kind="final_response",
                    user_id=input.user_id
                )
            else:
                tool_calls = event.get_function_calls()
                logger.info(f"Tool calls: {tool_calls}")
                tool_responses = event.get_function_responses()
                logger.info(f"Tool responses: {tool_responses}")
                if tool_responses:
                    for tool_response in tool_responses:
                        yield ChatOutput(
                            message=tool_response.name,
                            content=tool_response.model_dump_json(),
                            thread_id=input.thread_id,
                            kind="tool_message",
                            user_id=input.user_id,
                            role="tool"
                        )
                elif tool_calls:
                    total_satoshis = 0
                    for tool_call in tool_calls:
                        satoshis = tool_to_sats_map.get(tool_call.name, 0)
                        logger.debug(f'Tool call: {tool_call.name}, satoshis: {satoshis}')
                        total_satoshis += satoshis
                    if total_satoshis > 0:
                        yield ChatOutput(
                            message=f"Tool call requires payment: {tool_call.name}",
                            content=event.model_dump_json(),
                            thread_id=input.thread_id,
                            kind="requires_payment",
                            user_id=input.user_id,
                            satoshis=total_satoshis
                        )
                else:
                    logger.info(f"Unknown event type: {event}")
    
    return chat_generator