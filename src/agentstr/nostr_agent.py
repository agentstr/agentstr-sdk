

from agentstr.models import AgentCard, ChatInput, ChatOutput
from agentstr.a2a import PriceHandler, PriceHandlerResponse
from typing import Callable


class NostrAgent:
    def __init__(self, 
                 agent_card: AgentCard, 
                 agent_callable: Callable[[ChatInput], ChatOutput],
                 price_handler: PriceHandler):
        self.agent_card = agent_card
        self.agent_callable = agent_callable
        self.price_handler = price_handler

    async def chat(self, message: ChatInput) -> ChatOutput:
        return await self.agent_callable(message)

    async def estimate_price(self, message: ChatInput) -> PriceHandlerResponse | None:
        """Estimate the price of a message."""
        if not self.price_handler:
            satoshis = (self.agent_card.satoshis or 0) if self.agent_card else 0
            return PriceHandlerResponse(can_handle=True, satoshi_estimate=satoshis, user_message="")
        return await self.price_handler.handle(message, self.agent_card)
