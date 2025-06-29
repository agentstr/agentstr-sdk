import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentstr.agents.providers.langgraph import langgraph_chat_generator
from agentstr.mcp.providers.langgraph import to_langgraph_tools
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.nostr_client import NostrClient
from agentstr.agents.nostr_agent import NostrAgent
from agentstr.agents.nostr_agent_server import NostrAgentServer
from agentstr.models import AgentCard, Metadata
from agentstr.database import BaseDatabase, Database
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class StratumAgent:
    """A high-level class for streamlining agentstr agent creation on nostr.

    This class simplifies the process of creating and running an agentstr agent
    on the nostr network. It handles the setup of the agent, including its
    connection to the nostr network, integration with MCPs (Model Control Protocol),
    and state persistence.

    Key Features:
        - Streamlined agent creation with minimal configuration.
        - Support for state persistence using PostgreSQL or SQLite.
        - Integration with Nostr MCP Servers for extended capabilities.
        - Out-of-the-box support for features like streaming payments and
          human-in-the-loop interactions.
    """
    def __init__(self,
                 nostr_client: NostrClient,
                 name: str = "Stratum Agent",
                 description: str = "A helpful assistant.",
                 prompt: str = "You are a helpful assistant.",
                 satoshis: int = 0,
                 nostr_mcp_pubkeys: list[str] = [],
                 nostr_mcp_clients: list[NostrMCPClient] = [],
                 agent_card: AgentCard = None,
                 nostr_metadata: Metadata | None = None,
                 database: BaseDatabase | None = None,
                 checkpointer: AsyncPostgresSaver | AsyncSqliteSaver | None = None):
        """Initializes the StratumAgent.

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
            checkpointer: The checkpointer for saving agent state.
        """
        self._check_env_vars()
        if nostr_client is None:
            raise ValueError("nostr_client is required")
        self.nostr_client = nostr_client
        self.nostr_mcp_clients = nostr_mcp_clients.copy() if nostr_mcp_clients else []
        for mcp_pubkey in nostr_mcp_pubkeys:
            self.nostr_mcp_clients.append(NostrMCPClient(nostr_client=nostr_client,
                                                         mcp_pubkey=mcp_pubkey))
        self.database = database or Database()
        self.agent_card = agent_card
        self.nostr_metadata = nostr_metadata
        self.prompt = prompt
        self.checkpointer = checkpointer
        self.name = name
        self.description = description
        self.satoshis = satoshis

    def _check_env_vars(self):
        """Checks for required environment variables."""
        if os.getenv("LLM_BASE_URL") is None:
            raise ValueError("LLM_BASE_URL is not set")
        if os.getenv("LLM_API_KEY") is None:
            raise ValueError("LLM_API_KEY is not set")
        if os.getenv("LLM_MODEL_NAME") is None:
            raise ValueError("LLM_MODEL_NAME is not set")
        
    async def _create_agent_server(self):
        """Creates and configures the NostrAgentServer."""
        all_tools = []
        for nostr_mcp_client in self.nostr_mcp_clients:
            all_tools.extend(await to_langgraph_tools(nostr_mcp_client))

        all_skills = [await nostr_mcp_client.get_skills() for nostr_mcp_client in self.nostr_mcp_clients]

        if self.checkpointer is None:
            if self.database.conn_str.startswith("postgres"):
                self.checkpointer = AsyncPostgresSaver(self.database.conn_str)
            elif self.database.conn_str.startswith("sqlite"):
                self.checkpointer = AsyncSqliteSaver(self.database.conn_str)
            else:
                raise ValueError(f"Unsupported connection string: {self.database.conn_str}")

        await self.checkpointer.setup()

        # Create react agent
        agent = create_react_agent(
            model=ChatOpenAI(temperature=0,
                            base_url=os.getenv("LLM_BASE_URL"),
                            api_key=os.getenv("LLM_API_KEY"),
                            model_name=os.getenv("LLM_MODEL_NAME")),
            tools=all_tools,
            prompt=self.prompt,
            checkpointer=self.checkpointer,
        )

        chat_generator = langgraph_chat_generator(agent, self.nostr_mcp_clients)

        # Create Nostr Agent
        nostr_agent = NostrAgent(
            agent_card=self.agent_card or AgentCard(
                name=self.name, 
                description=self.description, 
                skills=all_skills, 
                satoshis=self.satoshis),
            chat_generator=chat_generator)

        # Create Nostr Agent Server
        server = NostrAgentServer(nostr_client=self.nostr_client,
                                  nostr_agent=nostr_agent,
                                  nostr_metadata=self.nostr_metadata)

        return server

    async def start(self):
        """Starts the agent server."""
        server = await self._create_agent_server()
        await server.start()