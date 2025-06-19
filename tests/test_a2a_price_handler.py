from dotenv import load_dotenv

load_dotenv()

import os
import pytest
import pytest_asyncio

from agentstr.a2a import AgentCard, Skill, default_price_handler, PriceHandlerResponse

# These tests intentionally hit a live LLM endpoint so that we can see the end-to-end behavior
# of the PriceHandler.  They are skipped automatically if the needed environment variables
# (LLM_API_KEY at minimum) are not present so that CI environments that do not have
# credentials do not fail.

REQUIRED_ENV_VARS = ["LLM_API_KEY", "LLM_MODEL_NAME", "LLM_BASE_URL"]


def _have_llm_creds() -> bool:
    """Return True if all required LLM environment variables are present."""
    return all(os.getenv(var) for var in REQUIRED_ENV_VARS)


@pytest.fixture(scope="module")
def price_handler():
    if not _have_llm_creds():
        pytest.skip("LLM credential environment variables missing – skipping live LLM tests.")

    # default_price_handler will pick up the remaining configuration (base_url, model_name, etc.)
    # from environment variables if they are set.  This keeps the test flexible for different
    # developer setups.
    return default_price_handler(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        model_name=os.getenv("LLM_MODEL_NAME"),
    )


@pytest_asyncio.fixture
async def agent_card() -> AgentCard:
    """Create a simple AgentCard with a couple of priced skills."""
    return AgentCard(
        name="TestAgent",
        description="An agent that tells jokes and converts currencies.",
        skills=[
            Skill(name="tell_joke", description="Tell a dad joke", satoshis=5),
            Skill(name="convert_currency", description="Convert between currencies", satoshis=2),
        ],
        satoshis=1,  # Base price for any interaction
        nostr_pubkey="pubkey123",
        nostr_relays=[],
    )


@pytest.mark.asyncio
async def test_price_handler_handle_joke(price_handler, agent_card):
    """Ensure the handler returns a valid PriceHandlerResponse for a joke request."""
    user_message = "Can you tell me a dad joke?"
    response: PriceHandlerResponse = await price_handler.handle(user_message, agent_card)

    # We cannot assert the exact content as it depends on the LLM, but we can verify structure.
    assert isinstance(response, PriceHandlerResponse)
    assert isinstance(response.can_handle, bool)
    assert isinstance(response.cost_sats, int)
    assert isinstance(response.user_message, str)
    assert isinstance(response.skills_used, list)
    assert response.cost_sats == 5
    assert response.skills_used == ["tell_joke"]

    # Output some useful information for debugging when running locally.
    # This will only show if the test is run with -s or if the test fails.
    print("LLM response:", response.model_dump_json())


@pytest.mark.asyncio
async def test_price_handler_unrelated_request(price_handler, agent_card):
    """Ask something completely unrelated to test the negative path."""
    user_message = "What's the weather on Mars right now?"
    response: PriceHandlerResponse = await price_handler.handle(user_message, agent_card)

    assert isinstance(response, PriceHandlerResponse)
    # Whether the agent can handle or not depends on the LLM; we just check types.
    assert isinstance(response.can_handle, bool)
    assert isinstance(response.user_message, str)
    assert isinstance(response.skills_used, list)
    assert response.cost_sats == 0
    assert response.skills_used == []

    print("LLM response (unrelated):", response.model_dump_json())