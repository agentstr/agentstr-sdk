from typing import Callable
from agno.agent import Agent
from agentstr.models import ChatInput, ChatOutput


def agno_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    async def agent_callable(input: ChatInput):
        return (await agent.arun(
            message=input.message,
            session_id=input.thread_id,
            user_id=input.user_id,
        )).content
    return agent_callable