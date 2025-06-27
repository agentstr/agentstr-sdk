import json
import yaml
from pydantic import BaseModel
from agentstr.logger import get_logger
from pynostr.metadata import Metadata
from typing import Any

logger = get_logger(__name__)


def to_metadata_yaml(path: str) -> Metadata:
    """Utility function to convert a metadata file to a Metadata object."""
    with open(path, 'r') as f:
        return Metadata.from_dict(yaml.safe_load(f))


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