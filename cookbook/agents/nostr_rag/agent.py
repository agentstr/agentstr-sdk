from dotenv import load_dotenv

load_dotenv()

import os

from langchain_openai import ChatOpenAI

from agentstr import NostrRAG
from agentstr.nostr_rag import Author
from agentstr import NostrAgentServer, AgentCard, Skill, ChatInput, PrivateKey

# Define relays
relays   = os.getenv("NOSTR_RELAYS").split(",")

# Define LLM
model = ChatOpenAI(temperature=0,
                   base_url=os.getenv("LLM_BASE_URL"),
                   api_key=os.getenv("LLM_API_KEY"),
                   model_name=os.getenv("LLM_MODEL_NAME"))


async def agent_server():
    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        # Create the RAG instance
        rag = NostrRAG(relays=relays,
                       llm=model,
                       known_authors=[
                            Author(name="Lyn Alden", pubkey="npub1a2cww4kn9wqte4ry70vyfwqyqvpswksna27rtxd8vty6c74era8sdcw83a"),
                            Author(name="Saifedean Ammous", pubkey="npub1gdu7w6l6w65qhrdeaf6eyywepwe7v7ezqtugsrxy7hl7ypjsvxksd76nak"),
                            Author(name="Jack Dorsey", pubkey="npub1sg6plzptd64u62a878hep2kev88swjh3tw00gjsfl8f237lmu63q0uf63m")
                       ])
        return await rag.query(question=input.messages[-1], limit=8, query_type="authors")

    # Create Nostr Agent Server
    server = NostrAgentServer(relays=os.getenv("NOSTR_RELAYS").split(","),
                              private_key=os.getenv("AGENT_PRIVATE_KEY"),
                              agent_info=AgentCard(
                                  name='Nostr Search Agent',
                                  description='This agent can search Nostr social media for content by authors or hashtags.',
                                  skills=[Skill(
                                    name='nostr_search', 
                                    description='Search Nostr social media for content by authors or hashtags.', 
                                    satoshis=0
                                  )],
                                  satoshis=0,
                                  nostr_pubkey=PrivateKey.from_nsec(os.getenv('AGENT_PRIVATE_KEY')).public_key.bech32(),
                              ),
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
