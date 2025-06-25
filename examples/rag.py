from dotenv import load_dotenv

load_dotenv()

import os

from langchain_openai import ChatOpenAI

from agentstr import NostrRAG
from agentstr.agents.nostr_rag import Author

# Define relays
relays   = os.getenv("NOSTR_RELAYS").split(",")

# Define LLM
model = ChatOpenAI(temperature=0,
                   base_url=os.getenv("LLM_BASE_URL"),
                   api_key=os.getenv("LLM_API_KEY"),
                   model_name=os.getenv("LLM_MODEL_NAME"))

# Create the RAG instance
rag = NostrRAG(relays=relays,
               llm=model,
               known_authors=[
                    Author(name="Lyn Alden", pubkey="npub1a2cww4kn9wqte4ry70vyfwqyqvpswksna27rtxd8vty6c74era8sdcw83a"),
                    Author(name="Saifedean Ammous", pubkey="npub1gdu7w6l6w65qhrdeaf6eyywepwe7v7ezqtugsrxy7hl7ypjsvxksd76nak"),
                    Author(name="Jack Dorsey", pubkey="npub1sg6plzptd64u62a878hep2kev88swjh3tw00gjsfl8f237lmu63q0uf63m")
               ])

# Run a RAG query
async def run():
    result = await rag.query(question="what's new with Lyn Alden?", limit=8, query_type="authors")
    print(result)
    result = await rag.query(question="what's new with Jack?", limit=8, query_type="authors")
    print(result)
    result = await rag.query(question="What's new with Bitcoin?", limit=8, query_type="hashtags")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
