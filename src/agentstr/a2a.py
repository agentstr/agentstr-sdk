
import dspy

from agentstr.logger import get_logger
from agentstr.models import AgentCard, CanHandleResponse, PriceHandlerResponse

logger = get_logger(__name__)



CHAT_HISTORY = {}  # Thread id -> [str]


class CanHandlePrompt(dspy.Signature):
    """Analyze if the agent can handle this request based on their skills and description and chat history.
Consider both the agent's capabilities and whether the request matches their purpose."""
    user_request: str = dspy.InputField(desc="The user's request")
    agent_card: AgentCard = dspy.InputField(desc="The agent's model card")
    history: dspy.History = dspy.InputField(desc="The conversation history")
    user_response: CanHandleResponse = dspy.OutputField(
        desc=(
                "Message that explains why the agent can or cannot handle the request."
            )
        )

class PriceHandlerPrompt(dspy.Signature):
    """Assuming the agent can handle this request, determine the cost in satoshis.

The agent may need to use multiple skills to handle the request. If so, include all relevant skills.

The user_message should be a friendly, conversational message that:
- Confirms the action to be taken
- Explains what will be done in simple terms
- Is concise (1-2 sentences max)"""

    user_request: str = dspy.InputField(desc="The user's request")
    agent_card: AgentCard = dspy.InputField(desc="The agent's model card")
    history: dspy.History = dspy.InputField(desc="The conversation history")
    user_response: PriceHandlerResponse = dspy.OutputField(
        desc=(
                "Message that summarizes the process result, and the information users need, e.g., the "
                "confirmation_number if a new flight is booked."
            )
        )
    satoshis_estimate: int = dspy.OutputField(
        desc="Estimated cost in satoshis for the request"
    )



class PriceHandler:
    def __init__(self, llm_api_key: str, llm_model_name: str, llm_base_url: str):
        self.llm = dspy.LM(model=llm_model_name, api_base=llm_base_url.rstrip('/v1'), api_key=llm_api_key, model_type='chat')


    async def handle(self, user_message: str, agent_card: AgentCard, thread_id: str | None = None) -> PriceHandlerResponse:
        """Determine if an agent can handle a user's request and calculate the cost.

        This function uses an LLM to analyze whether the agent's skills match the user's request
        and returns the cost in satoshis if the agent can handle it.

        Args:
            user_message: The user's request message.
            agent_card: The agent's model card.
            thread_id: Optional thread ID for conversation context.

        Returns:
            PriceHandlerResponse
        """

        # check history
        if thread_id and thread_id in CHAT_HISTORY:
            user_message = f"{CHAT_HISTORY[thread_id]}\n\n{user_message}"
        if thread_id:
            CHAT_HISTORY[thread_id] = user_message

        logger.debug(f"Agent router: {user_message}")
        logger.debug(f"Agent card: {agent_card.model_dump()}")

        # Get the LLM response
        dspy.settings.configure(lm=self.llm)
        module = dspy.ChainOfThought(CanHandlePrompt)
        result: CanHandlePrompt = await module.acall(user_request=user_message, agent_card=agent_card, history=dspy.History(messages=[]))

        logger.info(f"LLM input: {user_message}, {agent_card.model_dump_json()}")
        logger.info(f"LLM response: {result.user_response.model_dump_json()}")

        if not result.user_response.can_handle:
            logger.info(f"Agent cannot handle request: {result.user_response.user_message}")
            return PriceHandlerResponse(
                can_handle=False,
                cost_sats=0,
                user_message=result.user_response.user_message,
                skills_used=[],
            )

        # Get the LLM response
        dspy.settings.configure(lm=self.llm)
        module = dspy.ChainOfThought(PriceHandlerPrompt)
        result: PriceHandlerPrompt = await module.acall(user_request=user_message, agent_card=agent_card, history=dspy.History(messages=[]))

        logger.info(f"Agent can handle request: {result.user_response.model_dump_json()}")
        logger.info(f"Estimated satoshis: {result.satoshis_estimate}")

        return PriceHandlerResponse(
            can_handle=True,
            cost_sats=result.satoshis_estimate,
            user_message=result.user_response.user_message,
            skills_used=result.user_response.skills_used,
        )



def default_price_handler(base_url: str, api_key: str, model_name: str) -> PriceHandler:
    """Create a default price handler using the given LLM parameters."""
    return PriceHandler(
        llm_api_key=api_key,
        llm_model_name=model_name,
        llm_base_url=base_url,
    )
