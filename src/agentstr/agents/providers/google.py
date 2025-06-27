from typing import Callable
from google.adk.agents import Agent
from agentstr.models import ChatInput, ChatOutput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentstr.logger import get_logger

logger = get_logger(__name__)

def google_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    # Session and Runner
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name='nostr_example', session_service=session_service)

    async def agent_callable(input: ChatInput):
        content = types.Content(role='user', parts=[types.Part(text=input.message)])
        await session_service.create_session(app_name='nostr_example', user_id=input.thread_id, session_id=input.thread_id)
        events_async = runner.run_async(user_id=input.thread_id,
                                        session_id=input.thread_id,
                                        new_message=content)
        async for event in events_async:
            logger.debug(f'Received event: {event}')
            if event.is_final_response():
                final_response = event.content.parts[0].text
                logger.debug("Agent Response: %s", final_response)
                return final_response
        return None
    return agent_callable
