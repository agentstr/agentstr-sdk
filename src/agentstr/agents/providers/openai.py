from typing import Callable
from agents import Runner, Agent
from agentstr.models import ChatInput, ChatOutput
from agentstr.logger import get_logger

logger = get_logger(__name__)

def openai_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    async def agent_callable(input: ChatInput) -> str:
        result = await Runner.run(agent, input=input.message)
        return result.final_output
    return agent_callable
