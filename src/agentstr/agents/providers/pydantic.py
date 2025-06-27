from typing import Callable
from pydantic_ai import Agent
from agentstr.models import ChatInput, ChatOutput


def pydantic_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.run(input.message)
        return result.output
    return agent_callable
