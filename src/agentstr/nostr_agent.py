

from pynostr.metadata import Metadata
from agentstr.models import AgentCard, ChatInput, ChatOutput
from typing import Callable, AsyncGenerator
from agentstr.logger import get_logger

logger = get_logger(__name__)

class NostrAgent:
    def __init__(self, 
                 agent_card: AgentCard,
                 nostr_metadata: Metadata | None = None,
                 chat_generator: Callable[[ChatInput], AsyncGenerator[ChatOutput, None]] = None,
                 agent_callable: Callable[[ChatInput], ChatOutput | str] = None):
        if chat_generator is None and agent_callable is None:
            raise ValueError("Must provide either chat_generator or agent_callable")
        self.agent_card = agent_card
        self.nostr_metadata = nostr_metadata
        self.chat_generator = chat_generator
        self.agent_callable = agent_callable

    async def chat_stream(self, message: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        """Send a message to the agent and retrieve the response as a stream."""
        if self.chat_generator:
            logger.info(f"Received input: {message.model_dump()}")
            async for chunk in self.chat_generator(message):
                logger.info(f"Chunk: {chunk}")           
                yield chunk
        elif self.agent_callable:
            logger.info(f"Received input: {message.model_dump()}")
            response = self.agent_callable(message)
            if isinstance(response, str):
                response = ChatOutput(
                    message=response, 
                    thread_id=message.thread_id, 
                    user_id=message.user_id,
                    role="agent",
                    satoshis=0,
                    kind="final_response",
                    agent_name=self.agent_card.name
                )
            logger.info(f"Response: {response}")
            yield response
