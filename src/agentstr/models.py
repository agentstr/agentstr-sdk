from typing import Any
from pydantic import BaseModel


class NoteFilters(BaseModel):
    """Filters for filtering Nostr notes/events."""
    nostr_pubkeys: list[str] | None = None  #: Filter by specific public keys
    nostr_tags: list[str] | None = None  #: Filter by specific tags
    following_only: bool = False  #: Only show notes from followed users (not implemented)


class Skill(BaseModel):
    """Represents a specific capability or service that an agent can perform.

    A Skill defines a discrete unit of functionality that an agent can provide to other
    agents or users. Skills are the building blocks of an agent's service offerings and
    can be priced individually to create a market for agent capabilities.

    Attributes:
        name (str): A unique identifier for the skill that should be descriptive and
            concise. This name is used for referencing the skill in agent interactions.
        description (str): A detailed explanation of what the skill does, including:
            - The specific functionality provided
            - How to use the skill
            - Any limitations or prerequisites
            - Expected inputs and outputs
        satoshis (int, optional): The price in satoshis for using this skill. This allows
            agents to:
            - Set different prices for different capabilities
            - Create premium services
            - Implement usage-based pricing
            If None, the skill is either free or priced at the agent's base rate.
    """

    name: str
    description: str
    satoshis: int | None = None


class AgentCard(BaseModel):
    """Represents an agent's profile and capabilities in the Nostr network.

    An AgentCard is the public identity and capabilities card for an agent in the Nostr
    network. It contains essential information about the agent's services, pricing,
    and communication endpoints.

    Attributes:
        name (str): A human-readable name for the agent. This is the agent's display name.
        description (str): A detailed description of the agent's purpose, capabilities,
            and intended use cases.
        skills (list[Skill]): A list of specific skills or services that the agent can perform.
            Each skill is represented by a Skill model.
        satoshis (int, optional): The base price in satoshis for interacting with the agent.
            If None, the agent may have free services or use skill-specific pricing.
        nostr_pubkey (str): The agent's Nostr public key. This is used for identifying
            and communicating with the agent on the Nostr network.
        nostr_relays (list[str]): A list of Nostr relay URLs that the agent uses for
            communication. These relays are where the agent publishes and receives messages.
    """

    name: str
    description: str
    skills: list[Skill] = []
    satoshis: int | None = None
    nostr_pubkey: str
    nostr_relays: list[str] = []


class ChatInput(BaseModel):
    """Represents input data for an agent-to-agent chat interaction.

    Attributes:
        messages (list[str]): A list of messages in the conversation.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        extra_inputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """

    messages: list[str]
    thread_id: str | None = None
    extra_inputs: dict[str, Any] = {}


class ChatOutput(BaseModel):
    """Represents output data for an agent chat interaction.
    
    Attributes:
        message (str): The message to send to the user.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        satoshis_used: (int, optional): The amount of satoshis used for the request. Defaults to None.
        extra_outputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """
    message: str
    thread_id: str | None = None
    satoshis_used: int | None = None
    extra_outputs: dict[str, Any] = {}


class PriceHandlerResponse(BaseModel):
    """Response model for the price handler.

    Attributes:
        can_handle: Whether the agent can handle the request
        cost_sats: Total cost in satoshis (0 if free or not applicable)
        user_message: Friendly message to show the user about the action to be taken
        skills_used: List of skills that would be used, if any
    """
    can_handle: bool
    cost_sats: int = 0
    user_message: str = ""
    skills_used: list[str] = []


class CanHandleResponse(BaseModel):
    """Response model for the can handle handler.

    Attributes:
        can_handle: Whether the agent can handle the request
        user_message: Friendly message to explain why the agent can or cannot handle the request
    """
    can_handle: bool
    user_message: str = ""
