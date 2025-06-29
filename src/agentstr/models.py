from typing import Any, Literal, Callable
import json
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pynostr.metadata import Metadata  # noqa: F401


class Tool(BaseModel):
    """Represents a tool that an agent can use to perform a specific action."""
    fn: Callable[..., Any]
    name: str
    description: str
    input_schema: dict[str, Any]
    satoshis: int | None = None


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
    """

    name: str
    description: str
    satoshis: int | None = None


class AgentCard(BaseModel):
    """Represents an agent's profile and capabilities in the Nostr network.

    An AgentCard is the public identity and capabilities card for an agent in the Nostr
    network. It contains essential information about the agent's services, pricing,
    and communication endpoints.
    """

    name: str
    description: str
    skills: list[Skill] = []
    satoshis: int | None = None
    nostr_pubkey: str | None = None
    nostr_relays: list[str] = []


class User(BaseModel):
    """Simple user model persisted by the database layer."""

    user_id: str
    available_balance: int = 0
    current_thread_id: str | None = None


class Message(BaseModel):
    """Represents a message in a chat interaction. This should only be retrieved from the Database, not created manually."""

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
    def from_row(cls, row: Any) -> "Message":
        if row is None:
            raise ValueError("Row cannot be None")
        def parse_json_field(val):
            if val is None or val == "":
                return {}
            if isinstance(val, dict):
                return val
            try:
                return json.loads(val)
            except Exception:
                return {}
        created_at = row["created_at"]
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except Exception:
                created_at = datetime.now(timezone.utc)
        return cls(
            agent_name=row["agent_name"],
            thread_id=row["thread_id"],
            idx=row["idx"],
            user_id=row["user_id"],
            role=row["role"],
            message=row.get("message", ""),
            content=row.get("content", ""),
            kind=row.get("kind", "request"),
            satoshis=row.get("satoshis"),
            extra_inputs=parse_json_field(row.get("extra_inputs")),
            extra_outputs=parse_json_field(row.get("extra_outputs")),
            created_at=created_at.astimezone(timezone.utc) if hasattr(created_at, "astimezone") else created_at,
        )


class ChatInput(BaseModel):
    """Represents input data for an agent chat interaction."""

    message: str
    thread_id: str | None = None
    user_id: str | None = None
    extra_inputs: dict[str, Any] = {}
    history: list[Message] = []


class ChatOutput(BaseModel):
    """Represents output data for an agent chat interaction."""
    message: str
    content: str
    thread_id: str | None = None
    user_id: str | None = None
    role: Literal["agent", "tool"] = "agent"
    kind: Literal["requires_payment", "tool_message", "requires_input", "final_response", "error"] = "final_response"
    satoshis: int | None = None
    extra_outputs: dict[str, Any] = {}