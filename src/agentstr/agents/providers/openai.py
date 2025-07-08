from typing import Callable
from agents import Runner, Agent
from typing import Callable, AsyncGenerator
from agentstr.models import ChatInput, ChatOutput
from agentstr.mcp.nostr_mcp_client import NostrMCPClient
from agentstr.logger import get_logger
from agents import Agent, ItemHelpers, Runner


logger = get_logger(__name__)

def openai_agent_callable(agent: Agent) -> Callable[[ChatInput], ChatOutput | str]:
    """Create a callable that can be used with the Agentstr framework.
    
    Args:
        agent: The OpenAI agent to wrap.
    
    Returns:
        A callable that can be used with the Agentstr framework.
    """
    async def agent_callable(input: ChatInput) -> str:
        result = await Runner.run(agent, input=input.message)
        return result.final_output
    return agent_callable


def openai_chat_generator(agent: Agent, mcp_clients: list[NostrMCPClient] | None = None) -> Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]:
    """Create a chat generator from an OpenAI agent.
    
    Note: this is not currently supported."""

    raise NotImplementedError("OpenAI chat generator is not currently supported")
    tool_to_sats_map = {}
    if mcp_clients is not None and len(mcp_clients) > 0:
        for mcp_client in mcp_clients:
            tool_to_sats_map.update(mcp_client.tool_to_sats_map)
    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        result = Runner.run_streamed(agent, input=input.message)
        async for event in result.stream_events():
            # We'll ignore the raw responses event deltas
            logger.info(f"Event: {event}")
            if event.type == "raw_response_event":
                if event.data.type == 'response.output_item.added':
                    if event.data.item.type == 'function_call':
                        total_satoshis = 0
                        tool_call = event.data.item.name
                        satoshis = tool_to_sats_map.get(tool_call, 0)
                        logger.info(f'Tool call: {tool_call}, satoshis: {satoshis}')
                        total_satoshis += satoshis
                        if total_satoshis > 0:
                            yield ChatOutput(
                                message=f"Tool call requires payment: {tool_call}",
                                content=event.data.item.model_dump_json(),
                                thread_id=input.thread_id,
                                kind="tool_message",
                                user_id=input.user_id,
                                role="tool",
                                satoshis=total_satoshis
                            )
                continue
            # When the agent updates, print that
            elif event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}")
                continue
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("-- Tool was called")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                elif event.item.type == "message_output_item":
                    print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                    yield ChatOutput(
                        message=ItemHelpers.text_message_output(event.item),
                        content=event.item.raw_item.model_dump_json(),
                        thread_id=input.thread_id,
                        kind="final_response",
                        user_id=input.user_id,
                        role="agent"
                    )
                else:
                    pass  # Ignore other event types
            else:
                logger.info(f"Unknown event type: {event.type}: {event}")
                continue
    return chat_generator