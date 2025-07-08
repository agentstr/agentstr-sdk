from typing import Callable
from agno.agent import Agent
from agentstr.models import ChatInput, ChatOutput


def agno_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    """Create a callable that can be used with the Agentstr framework.
    
    Args:
        agent: The Agno Agent to wrap.
    
    Returns:
        A callable that can be used with the Agentstr framework.
    """
    async def agent_callable(input: ChatInput) -> ChatOutput | str:
        return (await agent.arun(
            message=input.message,
            session_id=input.thread_id,
            user_id=input.user_id,
        )).content
    return agent_callable