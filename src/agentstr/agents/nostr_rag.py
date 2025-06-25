import json
from typing import Literal

from pynostr.event import Event
from pydantic import BaseModel

from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient

try:
    from langchain_community.embeddings import FakeEmbeddings
    from langchain_core.documents import Document
    from langchain_core.messages import HumanMessage
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_openai import ChatOpenAI
    langchain_installed = True
except ImportError:
    FakeEmbeddings = "FakeEmbeddings"
    InMemoryVectorStore = "InMemoryVectorStore"
    Document = "Document"
    HumanMessage = "HumanMessage"
    ChatOpenAI = "ChatOpenAI"
    langchain_installed = False

logger = get_logger(__name__)


class Author(BaseModel):
    pubkey: str
    name: str | None = None


class NostrRAG:
    """Retrieval-Augmented Generation (RAG) system for Nostr events.

    This class fetches Nostr events, builds a vector store knowledge base, and enables
    semantic search and question answering over the indexed content.

    Examples
    --------
    Simple question answering over recent posts::

        import asyncio
        from langchain_openai import ChatOpenAI
        from agentstr import NostrRAG

        relays = ["wss://relay.damus.io"]
        rag = NostrRAG(relays=relays, llm=ChatOpenAI(model_name="gpt-3.5-turbo"))

        async def main():
            answer = await rag.query(question="What's new with Bitcoin?", limit=8)
            print(answer)

        asyncio.run(main())

    Full runnable script: `rag.py <https://github.com/agentstr/agentstr-sdk/tree/main/examples/rag.py>`_
    """
    def __init__(self, nostr_client: NostrClient | None = None, vector_store=None, relays: list[str] | None = None,
                 private_key: str | None = None, nwc_str: str | None = None, embeddings=None, llm=None, llm_model_name=None, llm_base_url=None, llm_api_key=None,
                 known_authors: list[Author] | None = None):
        """Initialize the NostrRAG system.
        
        Args:
            nostr_client: An existing NostrClient instance (optional).
            vector_store: An existing vector store instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key in 'nsec' format (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            embeddings: Embedding model for vectorizing documents (defaults to FakeEmbeddings with size 256).
            llm: Language model (optional).
            llm_model_name: Name of the language model to use (optional).
            llm_base_url: Base URL for the language model (optional).
            llm_api_key: API key for the language model (optional).
            
        Raises:
            ImportError: If LangChain is not installed.
        """
        if not langchain_installed:
            logger.error("Langchain not found. Please install it to use NostrRAG. `pip install agentstr-sdk[rag]`")
            raise ImportError("Langchain not found. Please install it to use NostrRAG. `pip install agentstr-sdk[rag]`")
        self.nostr_client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.embeddings = embeddings or FakeEmbeddings(size=256)
        self.vector_store = vector_store or InMemoryVectorStore(self.embeddings)
        self.known_authors = known_authors or []
        self.known_authors_name_to_pubkey = {author.name: author.pubkey for author in self.known_authors}
        if llm is None and llm_model_name is None:
            raise ValueError("llm or llm_model_name must be provided")
        self.llm = llm or ChatOpenAI(model_name=llm_model_name, base_url=llm_base_url, api_key=llm_api_key, temperature=0)

    async def _select_author(self, question: str) -> tuple[str, str]:
        """Select relevant users for the given question.

        Args:
            question: The question to find a relevant user in

        Returns:
            The selected user's name
        """
        template = """
You are an user selector for Nostr. Given a question, suggest the relevant user mentioned in the question.
You must select from the list of known users.
Return ONLY the users in a JSON array format, like: ["Lyn Alden"] or ["Saifedean Ammous"]
Only respond with 1 user. If no user is mentioned, return an empty array.

Question: {question}

Known users: {users}
"""

        prompt = template.format(question=question, users=json.dumps([author.name for author in self.known_authors]))
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        try:
            authors = json.loads(response.content)
            if len(authors) == 0:
                return None, None
            elif authors[0] in self.known_authors_name_to_pubkey:
                return authors[0], self.known_authors_name_to_pubkey[authors[0]]
            else:
                logger.warning(f"Selected author not found in known authors: {authors[0]}")
                return None, None
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract authors
            logger.warning(f"Failed to parse author selection response. Response: {response.content}")
            return None, None

    async def _select_hashtags(self, question: str, previous_hashtags: list[str] | None = None) -> list[str]:
        """Select relevant hashtags for the given question.

        Args:
            question: The user's question
            previous_hashtags: Previously used hashtags for this conversation

        Returns:
            List of relevant hashtags
        """
        template = """
You are a hashtag selector for Nostr. Given a question, suggest relevant hashtags that would help find relevant content.
Return ONLY the hashtags in a JSON array format, like: ["#hashtag1", "#hashtag2"]
Use at most 5 hashtags.

Question: {question}
Previous hashtags: {history}
"""

        history = json.dumps(previous_hashtags or [])
        prompt = template.format(question=question, history=history)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        try:
            hashtags = json.loads(response.content)
            return hashtags
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract hashtags
            text = response.content
            hashtags = []
            # Find hashtags in the text
            for word in text.split():
                if word.startswith("#"):
                    hashtags.append(word)
            return hashtags[:5]  # Return at most 5 hashtags

    def _process_event(self, event: Event) -> Document:
        """Process a Nostr event into a LangChain Document.
        Args:
            event: A Nostr event.
        Returns:
            Document: A LangChain Document with the event's content and ID.
        """
        content = event.content
        metadata = event.to_dict()
        metadata.pop("content")
        return Document(page_content=content, id=event.id, metadata=metadata)

    async def build_knowledge_base(self, question: str, limit: int = 10, query_type: Literal["hashtags", "authors"] = "hashtags") -> list[dict]:
        """Build a knowledge base from Nostr events relevant to the question.

        Args:
            question: The user's question to guide hashtag selection
            limit: Maximum number of posts to retrieve

        Returns:
            List of retrieved events
        """
        # Select relevant hashtags for the question
        if query_type == "hashtags":
            hashtags = await self._select_hashtags(question)
            hashtags = [hashtag.lstrip("#") for hashtag in hashtags]

            logger.info(f"Selected hashtags: {hashtags}")

            # Fetch events for each hashtag
            events = await self.nostr_client.read_posts_by_tag(tags=hashtags, limit=limit)
        elif query_type == "authors":
            name, pubkey = await self._select_author(question)
            if pubkey is None:
                return []
            events = await self.nostr_client.read_posts_by_author(pubkey=pubkey, limit=limit)
            for event in events:
                event.content = f"Posted by {name}:\n\n{event.content}"
        else:
            raise ValueError(f"Invalid query type: {query_type}")

        # Process events into documents
        documents = [self._process_event(event) for event in events]
        await self.vector_store.aadd_texts([doc.page_content for doc in documents])

        return events

    async def retrieve(self, question: str, limit: int = 5, query_type: Literal["hashtags", "authors"] = "hashtags") -> list[Document]:
        """Retrieve relevant documents from the knowledge base.

        Args:
            question: The user's question
            limit: Maximum number of documents to retrieve
            query_type: Type of query to use (hashtags or authors)

        Returns:
            List of retrieved documents
        """
        await self.build_knowledge_base(question, limit=limit, query_type=query_type)
        return await self.vector_store.asimilarity_search(question, k=limit)

    async def query(self, question: str, limit: int = 5, query_type: Literal["hashtags", "authors"] = "hashtags") -> str:
        """Ask a question using the knowledge base.

        Args:
            question: The user's question
            limit: Number of documents to retrieve for context
            query_type: Type of query to use (hashtags or authors)

        Returns:
            The generated response
        """

        # Get relevant documents
        relevant_docs = await self.retrieve(question, limit, query_type)

        # Generate response using the LLM
        template = """
You are an expert assistant. Answer the following question based on the provided context.

Question: {question}

Context:
{context}

Answer:"""

        prompt = template.format(
            question=question,
            context="\n\n".join([doc.page_content for doc in relevant_docs]),
        )

        logger.info(f"Using prompt:\n{prompt}")

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
