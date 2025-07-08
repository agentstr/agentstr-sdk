


from langgraph.graph.graph import CompiledGraph
from typing import Callable, AsyncGenerator
from agentstr.models import ChatInput, ChatOutput
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.logger import get_logger

logger = get_logger(__name__)


def langgraph_agent_callable(agent: CompiledGraph) -> Callable[[ChatInput], ChatOutput | str]:
    async def agent_callable(input: ChatInput) -> ChatOutput | str:
        result = await agent.ainvoke(
            input={"messages": [{"role": "user", "content": input.message}]},
            config={
                "configurable": {
                    "thread_id": input.thread_id,
                    "user_id": input.user_id,
                    "checkpoint_ns": agent.name,
                }
            },
        )
        logger.info(f'Langgraph callable result: {result}')
        return result['messages'][-1].content
    return agent_callable


def langgraph_chat_generator(agent: CompiledGraph, mcp_clients: list[NostrMCPClient] | None = None) -> Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]:
    """Create a chat generator from a LangGraph graph. Supports human-in-the-loop and streaming payments.
    
    Args:
        agent: The LangGraph graph to wrap.
        mcp_clients: A list of NostrMCPClient objects (optional).
    
    Returns:
        An async generator that can be used with the Agentstr framework.
    """

    tool_to_sats_map = {}
    if mcp_clients is not None and len(mcp_clients) > 0:
        for mcp_client in mcp_clients:
            tool_to_sats_map.update(mcp_client.tool_to_sats_map)
    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        async for chunk in agent.astream(
            input={"messages": [{"role": "user", "content": input.message}]},
            config={
                "configurable": {
                    "thread_id": input.thread_id,
                    "user_id": input.user_id,
                    "checkpoint_ns": agent.name,
                }
            },
            stream_mode="updates"
        ):
            logger.info(f'Chunk: {chunk}')
            if 'agent' in chunk:
                update = chunk['agent']['messages'][-1]
                if update.tool_calls:
                    total_satoshis = 0
                    for tool_call in update.tool_calls:
                        satoshis = tool_to_sats_map.get(tool_call['name'], 0)
                        logger.debug(f'Tool call: {tool_call["name"]}, satoshis: {satoshis}')
                        total_satoshis += satoshis
                    if total_satoshis > 0:
                        yield ChatOutput(
                            message=f"Tool call requires payment: {tool_call['name']}",
                            content=update.model_dump_json(),
                            thread_id=input.thread_id,
                            kind="requires_payment",
                            user_id=input.user_id,
                            satoshis=total_satoshis
                        )
                else:
                    yield ChatOutput(
                        message=update.content,
                        content=update.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="final_response",
                        user_id=input.user_id
                    )
            elif 'tools' in chunk:
                for message in chunk['tools']['messages']:
                    yield ChatOutput(
                        message=message.content,
                        content=message.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="tool_message",
                        user_id=input.user_id,
                        role="tool"
                    )
    
    return chat_generator