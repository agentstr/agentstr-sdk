from typing import Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


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


class User(BaseModel):
    """Simple user model persisted by the database layer."""

    user_id: str
    available_balance: int = 0
    current_thread_id: str | None = None


class Message(BaseModel):
    """Represents a message in a chat interaction."""

    agent_name: str
    thread_id: str
    user_id: str
    idx: int
    message: str
    content: str
    role: Literal["user", "agent", "tool"]
    kind: Literal["request", "requires_payment", "tool_message", "requires_input", "final_response", "error"]
    satoshis: int | None = None
    extra_inputs: dict[str, Any] = {}
    extra_outputs: dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def from_row(cls, row: Any) -> "Message":  # helper for Sqlite (tuple) or asyncpg.Record
        if row is None:
            raise ValueError("Row cannot be None")
        # Both sqlite and pg rows behave like dicts with keys
        return cls(
            agent_name=row["agent_name"],
            thread_id=row["thread_id"],
            idx=row["idx"],
            user_id=row["user_id"],
            role=row["role"],
            message=row["message"],
            content=row["content"],
            sent=row["sent"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            created_at=row["created_at"],
        )


class ChatInput(BaseModel):
    """Represents input data for an agent chat interaction.

    Attributes:
        message (str): The message to send to the agent.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        extra_inputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """

    message: str
    thread_id: str | None = None
    user_id: str | None = None
    extra_inputs: dict[str, Any] = {}


class ChatOutput(BaseModel):
    """Represents output data for an agent chat interaction.
    
    Attributes:
        message (str): The message to send to the user.
        content (str): Full JSON content of the output.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        user_id: (str, optional): The ID of the user. Defaults to None.
        kind: (str, optional): The output type. Defaults to "final_response"
        satoshis: (int, optional): The amount of satoshis used for the request. Defaults to None.
        extra_outputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """
    message: str
    content: str
    thread_id: str | None = None
    user_id: str | None = None
    role: Literal["agent", "tool"] = "agent"
    kind: Literal["requires_payment", "tool_message", "requires_input", "final_response", "error"] = "final_response"
    satoshis: int | None = None
    extra_outputs: dict[str, Any] = {}