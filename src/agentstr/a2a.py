
import dspy

from agentstr.database.base import BaseDatabase
from agentstr.logger import get_logger
from agentstr.models import AgentCard, PriceHandlerResponse

logger = get_logger(__name__)


class PriceHandlerPrompt(dspy.Signature):
    """Analyze if the agent can handle this request based on their skills and description and chat history.
Consider both the agent's capabilities and whether the request matches their purpose.

Then estimate the cost in satoshis.

The agent may need to use multiple skills to handle the request. If so, include all relevant skills in the response and satoshi estimate.

The user_message should be a friendly, conversational message that:
- Confirms the action to be taken
- Explains what will be done in simple terms
- Is concise (1-2 sentences max)"""

    agent_card: AgentCard = dspy.InputField(desc="The agent's model card")
    request: str = dspy.InputField(desc="The user's request")
    response: PriceHandlerResponse = dspy.OutputField(
        desc=(
                "Message that summarizes the process result, and the information users need, e.g., the "
                "confirmation_number if a new flight is booked."
            )
        )


class PriceHandler:
    def __init__(self, db: BaseDatabase, llm_api_key: str, llm_model_name: str, llm_base_url: str):
        self.db = db
        self.llm = dspy.LM(model=llm_model_name, api_base=llm_base_url.rstrip('/v1'), api_key=llm_api_key, model_type='chat')


    async def handle(self, user_message: str, agent_card: AgentCard) -> PriceHandlerResponse:
        """Determine if an agent can handle a user's request and calculate the cost.

        This function uses an LLM to analyze whether the agent's skills match the user's request
        and returns the cost in satoshis if the agent can handle it.

        Args:
            user_message: The user's request message.
            agent_card: The agent's model card.

        Returns:
            PriceHandlerResponse
        """

        # check history
        logger.debug(f"Agent router: {user_message}")
        logger.debug(f"Agent card: {agent_card.model_dump()}")

        # Get the LLM response
        dspy.settings.configure(lm=self.llm)
        module = dspy.ChainOfThought(PriceHandlerPrompt)
        result: PriceHandlerPrompt = await module.acall(request=user_message, agent_card=agent_card)

        logger.info(f"LLM input: {user_message}, {agent_card.model_dump_json()}")
        logger.info(f"LLM response: {result.response.model_dump_json()}")

        if not result.response.can_handle:
            logger.info(f"Agent cannot handle request: {result.response.user_message}")
            return PriceHandlerResponse(
                can_handle=False,
                satoshi_estimate=0,
                user_message=result.response.user_message,
                skills_used=[],
            )

        logger.info(f"Agent can handle request: {result.response.model_dump_json()}")
        return PriceHandlerResponse(
            can_handle=True,
            satoshi_estimate=result.response.satoshi_estimate,
            user_message=result.response.user_message,
            skills_used=result.response.skills_used,
        )



def default_price_handler(db: BaseDatabase, base_url: str, api_key: str, model_name: str) -> PriceHandler:
    """Create a default price handler using the given LLM parameters."""
    return PriceHandler(
        db=db,
        llm_api_key=api_key,
        llm_model_name=model_name,
        llm_base_url=base_url,
    )
