from dotenv import load_dotenv

load_dotenv()

import os
from agno.agent import Agent
from agno.tools.pubmed import PubmedTools
from agno.models.openai import OpenAIChat
from agentstr import NostrAgentServer, AgentCard, Skill, ChatInput, PrivateKey, default_price_handler


base_url = os.getenv("LLM_BASE_URL")
api_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME")


async def agent_server():
    # Define Agno agent
    agent = Agent(
        model=OpenAIChat(
            temperature=0,
            base_url=base_url,
            api_key=api_key,
            id=model_name,
        ),
        tools=[PubmedTools()],
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.arun(message=input.messages[-1], session_id=input.thread_id)
        return result.content

    # Create Nostr Agent Server
    server = NostrAgentServer(relays=os.getenv("NOSTR_RELAYS").split(","),
                              private_key=os.getenv("AGENT_PRIVATE_KEY"),
                              nwc_str=os.getenv("AGENT_NWC_CONN_STR"),
                              agent_info=AgentCard(
                                  name='Medical Agent',
                                  description='This agent can search and summarize medical articles in the PubMed database.',
                                  skills=[Skill(
                                    name='medical_search', 
                                    description='Search for medical articles in the PubMed database that matches users\' request.', 
                                    satoshis=0
                                  )],
                                  satoshis=15,
                                  nostr_pubkey=PrivateKey.from_nsec(os.getenv('AGENT_PRIVATE_KEY')).public_key.bech32(),
                              ),
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())