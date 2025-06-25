import json
from pydantic import BaseModel
from agentstr.logger import get_logger
from typing import Any

logger = get_logger(__name__)


def stringify_result(result: Any) -> str:
    """Convert a result to a string."""
    logger.debug(f"Stringifying result: {result}")
    if isinstance(result, dict) or isinstance(result, list):
        logger.debug("Result is dict or list")
        return json.dumps(result)
    elif isinstance(result, BaseModel):
        logger.debug("Result is BaseModel")
        return result.model_dump_json()
    else:
        logger.debug(f"Result is other type ({type(result)}): {result}")
        return str(result)