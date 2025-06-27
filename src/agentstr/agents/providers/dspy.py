import json
import dspy
from typing import AsyncGenerator, Callable
from agentstr.models import ChatInput, ChatOutput
from agentstr.mcp.nostr_mcp_client import NostrMCPClient

from agentstr.logger import get_logger
logger = get_logger(__name__)


class MyStatusMessageProvider(dspy.streaming.StatusMessageProvider):
    def module_end_status_message(self, outputs):
        logger.info(f"module_end_status_message Type of outputs: {type(outputs)}")
        response = {}
        for item in outputs:
            if item == "next_tool_name":
                response[item] = outputs.get(item)
            elif item == "next_tool_args":
                response[item] = outputs.get(item)
            logger.info(f"module_end_status_message Item: {item}: {outputs.get(item)}")
        return json.dumps(response)

def dspy_chat_generator(agent: dspy.Module, mcp_clients: list[NostrMCPClient], input_field: str = 'question',output_field: str = 'answer') -> Callable[[ChatInput], AsyncGenerator[ChatOutput, None]]:
    """Create a chat generator from a LangGraph graph."""
    tool_to_sats_map = {}
    if mcp_clients is not None and len(mcp_clients) > 0:
        for mcp_client in mcp_clients:
            tool_to_sats_map.update(mcp_client.tool_to_sats_map)

    agent_stream = dspy.streamify(agent, status_message_provider=MyStatusMessageProvider(), is_async_program=True)
    async def chat_generator(input: ChatInput) -> AsyncGenerator[ChatOutput, None]:
        async for chunk in agent_stream(**{input_field: input.message}):
            logger.info(f'Chunk: {chunk}')
            if isinstance(chunk, dspy.streaming.StreamResponse):
                pass
            elif isinstance(chunk, dspy.Prediction):
                return_value = getattr(chunk, output_field)
                yield ChatOutput(
                    message=return_value,
                    content=json.dumps(chunk.toDict()),
                    thread_id=input.thread_id,
                    kind="final_response",
                    user_id=input.user_id
                )
            elif isinstance(chunk, dspy.streaming.StatusMessage):
                if chunk.message:
                    try:
                        content = json.loads(chunk.message)
                        if "next_tool_name" in content:
                            tool_name = content["next_tool_name"]
                            satoshis = tool_to_sats_map.get(tool_name, 0)
                            logger.info(f'Tool call requires payment: {tool_name}, satoshis: {satoshis}')
                            yield ChatOutput(
                                message=f"Tool call requires payment: {tool_name}",
                                content=chunk.message,
                                thread_id=input.thread_id,
                                kind="requires_payment",
                                user_id=input.user_id,
                                satoshis=satoshis
                            )
                    except Exception as e:
                        logger.error(f'Error parsing status message: {e}')
    return chat_generator
