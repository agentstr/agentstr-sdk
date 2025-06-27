


from langgraph.graph.graph import CompiledGraph
from typing import Callable, AsyncGenerator
from agentstr.models import ChatInput, ChatOutput
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.logger import get_logger

logger = get_logger(__name__)

def langgraph_chat_generator(graph: CompiledGraph, mcp_clients: list[NostrMCPClient]) -> Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]:
    """Create a chat generator from a LangGraph graph."""
    tool_to_sats_map = {}
    if mcp_clients is not None and len(mcp_clients) > 0:
        for mcp_client in mcp_clients:
            tool_to_sats_map.update(mcp_client.tool_to_sats_map)
    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        async for chunk in graph.astream(
            {"messages": [{"role": "user", "content": input.message}]},
            stream_mode="updates"
        ):
            logger.debug(f'Chunk: {chunk}')
            if 'agent' in chunk:
                update = chunk['agent']['messages'][-1]
                if update.tool_calls:
                    total_satoshis = 0
                    for tool_call in update.tool_calls:
                        satoshis = tool_to_sats_map.get(tool_call['name'], 0)
                        logger.debug(f'Tool call: {tool_call["name"]}, satoshis: {satoshis}')
                        total_satoshis += satoshis
                    yield ChatOutput(
                        message=update.content,
                        content=update.content.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="requires_payment",
                        user_id=input.user_id,
                        satoshis=total_satoshis
                    )
                else:
                    yield ChatOutput(
                        message=update.content,
                        content=update.content.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="final_response",
                        user_id=input.user_id
                    )
            elif 'tools' in chunk:
                for message in chunk['tools']['messages']:
                    yield ChatOutput(
                        message=message.content,
                        content=update.content.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="tool_message",
                        user_id=input.user_id,
                        role="tool"
                    )
    
    return chat_generator