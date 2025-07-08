"""
Agent-Nostr integration layer.

Defines the NostrAgent class, which adapts an agent (such as an LLM or other callable)
to the Nostr chat protocol, supporting both streaming and non-streaming interfaces.
"""

from pynostr.metadata import Metadata
from agentstr.models import AgentCard, ChatInput, ChatOutput
from typing import Callable, AsyncGenerator
from agentstr.logger import get_logger

logger = get_logger(__name__)

class NostrAgent:
    """
    Adapter that exposes an agent as a Nostr-compatible chat interface.

    The NostrAgent class wraps an agent (either as a streaming generator or a callable)
    and exposes a unified streaming chat interface for use in the Nostr protocol.
    """
    def __init__(self, 
                 agent_card: AgentCard,
                 nostr_metadata: Metadata | None = None,
                 chat_generator: Callable[[ChatInput], AsyncGenerator[ChatOutput, None]] = None,
                 agent_callable: Callable[[ChatInput | str], ChatOutput | str] = None):
        """
        Initialize a NostrAgent.

        Args:
            agent_card (AgentCard): The agent's public profile and capabilities.
            nostr_metadata (Metadata, optional): Additional Nostr metadata for the agent.
            chat_generator (Callable, optional): Async generator for streaming responses.
            agent_callable (Callable, optional): Callable for non-streaming responses.

        Raises:
            ValueError: If neither chat_generator nor agent_callable is provided.
            ValueError: If agent_card is None.
        """
        if agent_card is None:
            raise ValueError("Must provide agent_card")
        if chat_generator is None and agent_callable is None:
            raise ValueError("Must provide either chat_generator or agent_callable")
        self.agent_card = agent_card
        self.nostr_metadata = nostr_metadata
        self.chat_generator = chat_generator
        self.agent_callable = agent_callable

    async def chat_stream(self, message: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        """
        Send a message to the agent and retrieve the response as a stream.

        Args:
            message (ChatInput): The chat input to send to the agent.

        Yields:
            ChatOutput: Each chunk of the agent's response.
        """
        if self.chat_generator:
            logger.info(f"Received input: {message.model_dump()}")
            async for chunk in self.chat_generator(message):
                logger.info(f"Chunk: {chunk}")           
                yield chunk
        elif self.agent_callable:
            logger.info(f"Received input: {message.model_dump()}")
            response = await self.agent_callable(message)
            if isinstance(response, str):
                response = ChatOutput(
                    message=response, 
                    content=response,
                    thread_id=message.thread_id, 
                    user_id=message.user_id,
                    role="agent",
                    satoshis=0,
                    kind="final_response",
                    extra_outputs={}
                )
            elif not isinstance(response, ChatOutput):
                raise ValueError(f"Response must be ChatOutput or str, got {type(response)}")
            logger.info(f"Response: {response}")
            yield response