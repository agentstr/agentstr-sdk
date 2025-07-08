from dotenv import load_dotenv

load_dotenv()

import os
from agentstr import NostrMCPServer, tool
from tavily import AsyncTavilyClient


@tool(satoshis=10)
async def web_search(query: str, num_results: int = 10) -> dict:
    """
    Search the web using Tavily Search API.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 10)

    Returns:
        A dictionary containing search results
    """
    print(f"Received query: {query}")
    # Get the Tavily API key from environment variables
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set")

    try:
        # Initialize Tavily client
        tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
        
        # Perform the search
        results = (await tavily_client.search(query, max_results=num_results, topic="news")).get('results', [])
        
        # Format results for MCP
        formatted_results = {
            "query": query,
            "num_results": num_results,
            "results": [
                {
                    "title": result.get('title', ''),
                    "content": result.get('content', ''),
                    "url": result.get('url', ''),
                    "snippet": result.get('snippet', ''),
                    "domain": result.get('domain', ''),
                    "rank": result.get('rank', 0)
                }
                for result in results
            ]
        }
        
        print(f"Search results: {formatted_results}")
        return formatted_results
    
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return {
            "error": f"Search failed: {str(e)}"
        }


# Get the environment variables
relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('MCP_SERVER_PRIVATE_KEY')
nwc_str = os.getenv('MCP_SERVER_NWC_CONN_STR')


async def run():
        # Create the MCP server
    server = NostrMCPServer(
        "Web Search Tool",
        relays=relays,
        private_key=private_key,
        nwc_str=nwc_str,
        tools=[web_search]
    )

    # Start the server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

