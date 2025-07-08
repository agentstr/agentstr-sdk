import os
from typing import Callable
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentstr.agents.providers.langgraph import langgraph_chat_generator
from agentstr.mcp.providers.langgraph import to_langgraph_tools
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.nostr_client import NostrClient
from agentstr.agents.nostr_agent import NostrAgent
from agentstr.agents.nostr_agent_server import NostrAgentServer
from agentstr.models import AgentCard, ChatInput, ChatOutput, Metadata
from agentstr.database import BaseDatabase, Database
from agentstr.commands.commands import DefaultCommands
from agentstr.commands.base import Commands
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class AgentstrAgent:
    """A high-level class for streamlining Agentstr agent creation on Nostr.

    This class simplifies the process of creating and running an Agentstr agent
    on the Nostr network. It handles the setup of the agent, including its
    connection to the Nostr network, integration with MCP (Model Context Protocol),
    and state persistence.

    Key Features:
        - Streamlined agent creation with minimal configuration.
        - Support for state persistence using PostgreSQL or SQLite.
        - Integration with Nostr MCP Servers for extended capabilities.
        - Out-of-the-box support for features like streaming payments and
          human-in-the-loop interactions.
    """
    def __init__(self,
                 nostr_client: NostrClient = None,
                 name: str = "Agentstr Agent",
                 description: str = "A helpful assistant.",
                 prompt: str = "You are a helpful assistant.",
                 satoshis: int = 0,
                 nostr_mcp_pubkeys: list[str] = [],
                 nostr_mcp_clients: list[NostrMCPClient] = [],
                 agent_card: AgentCard = None,
                 nostr_metadata: Metadata | None = None,
                 database: BaseDatabase | None = None,
                 commands: Commands | None = None,
                 checkpointer: AsyncPostgresSaver | AsyncSqliteSaver | None = None,
                 llm_model_name: str | None = None,
                 llm_base_url: str | None = None,
                 llm_api_key: str | None = None,
                 agent_callable: Callable[[ChatInput], ChatOutput | str] | None = None):
        """Initializes the AgentstrAgent.

        Args:
            nostr_client: The client for interacting with the nostr network.
            name: The name of the agent.
            description: A description of the agent.
            prompt: The system prompt for the agent.
            satoshis: The number of satoshis to charge per interaction.
            nostr_mcp_pubkeys: A list of public keys for Nostr MCP servers.
            nostr_mcp_clients: A list of pre-configured NostrMCPClient instances.
            agent_card: An AgentCard model with agent details.
            nostr_metadata: Metadata for the agent's nostr profile.
            database: The database for state persistence.
            commands: The commands for the agent.
            checkpointer: The checkpointer for saving agent state.
            llm_model_name: The name of the language model to use (or use environment variable LLM_MODEL_NAME).
            llm_base_url: The base URL for the language model (or use environment variable LLM_BASE_URL).
            llm_api_key: The API key for the language model (or use environment variable LLM_API_KEY).
            agent_callable: A callable for non-streaming responses (overrides default LLM response).
        """
        self.nostr_client = nostr_client or NostrClient()
        self.nostr_mcp_clients = nostr_mcp_clients.copy() if nostr_mcp_clients else []
        for mcp_pubkey in nostr_mcp_pubkeys:
            self.nostr_mcp_clients.append(NostrMCPClient(nostr_client=self.nostr_client,
                                                         mcp_pubkey=mcp_pubkey))
        self.database = database or Database()
        self.commands = commands or DefaultCommands(db=self.database, nostr_client=self.nostr_client, agent_card=agent_card)
        self.agent_card = agent_card
        self.nostr_metadata = nostr_metadata
        self.prompt = prompt
        self._checkpointer = checkpointer
        self.name = name
        self.description = description
        self.satoshis = satoshis
        self.llm_model_name = llm_model_name or os.getenv("LLM_MODEL_NAME")
        self.llm_base_url = llm_base_url or os.getenv("LLM_BASE_URL")
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY")
        self.agent_callable = agent_callable
        if self.agent_callable is None:
            # Require LLM
            self._check_llm_vars()

    def _check_llm_vars(self):
        """Checks for required environment variables."""
        if self.llm_model_name is None:
            raise ValueError("LLM_MODEL_NAME is not set")
        if self.llm_base_url is None:
            raise ValueError("LLM_BASE_URL is not set")
        if self.llm_api_key is None:
            raise ValueError("LLM_API_KEY is not set")        

    @property
    def checkpointer(self):
        """The checkpointer for saving agent state."""
        if self._checkpointer:
            return self._checkpointer
        checkpointer = None
        if self.database.conn_str.startswith("postgres"):
            checkpointer = AsyncPostgresSaver.from_conn_string(self.database.conn_str)
        elif self.database.conn_str.startswith("sqlite"):
            conn_str = self.database.conn_str.replace("sqlite://", "", 1)
            checkpointer = AsyncSqliteSaver.from_conn_string(conn_str)
        else:
            raise ValueError(f"Unsupported connection string: {self.database.conn_str}")
        return checkpointer

    
    async def _create_agent_server(self, checkpointer: AsyncPostgresSaver | AsyncSqliteSaver):
        """Creates and configures the NostrAgentServer."""
        all_tools = []
        for nostr_mcp_client in self.nostr_mcp_clients:
            all_tools.extend(await to_langgraph_tools(nostr_mcp_client))

        all_skills = [skill for skills in [await nostr_mcp_client.get_skills() for nostr_mcp_client in self.nostr_mcp_clients] for skill in skills]

        await checkpointer.setup()

        if self.agent_callable is not None:
            # Create dummy agent
            chat_generator = None
        else:            
            # Create react agent
            agent = create_react_agent(
                model=ChatOpenAI(temperature=0,
                                base_url=self.llm_base_url,
                                api_key=self.llm_api_key,
                                model_name=self.llm_model_name),
                tools=all_tools,
                prompt=self.prompt,
                checkpointer=checkpointer,
            )

            chat_generator = langgraph_chat_generator(agent, self.nostr_mcp_clients)

        # Create Nostr Agent
        nostr_agent = NostrAgent(
            agent_card=self.agent_card or AgentCard(
                name=self.name, 
                description=self.description, 
                skills=all_skills, 
                satoshis=self.satoshis),
            chat_generator=chat_generator,
            agent_callable=self.agent_callable,
            nostr_metadata=self.nostr_metadata)

        # Create Nostr Agent Server
        server = NostrAgentServer(nostr_client=self.nostr_client,
                                  nostr_agent=nostr_agent,
                                  db=self.database,
                                  commands=self.commands)

        return server

    async def start(self):
        """Starts the agent server."""
        async with self.checkpointer as checkpointer:
            server = await self._create_agent_server(checkpointer)
            await server.start()