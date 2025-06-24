

from agentstr.models import AgentCard, ChatInput, ChatOutput
from typing import Callable, AsyncGenerator
from agentstr.logger import get_logger

logger = get_logger(__name__)

class NostrAgent:
    def __init__(self, 
                 agent_card: AgentCard, 
                 chat_generator: Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]):
        self.agent_card = agent_card
        self.chat_generator = chat_generator

    async def chat_stream(self, message: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        """Send a message to the agent and retrieve the response as a stream."""
        logger.info(f"Received input: {message.model_dump()}")
        async for chunk in self.chat_generator(message):
            logger.info(f"Chunk: {chunk}")           
            yield chunk
