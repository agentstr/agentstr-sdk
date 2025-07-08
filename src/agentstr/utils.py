import json
import yaml
from pydantic import BaseModel
from agentstr.logger import get_logger
from pynostr.metadata import Metadata
from typing import Any
import os

logger = get_logger(__name__)


def default_metadata_file(path: str) -> str | None:
    """Utility function to find the default metadata file in the same directory as the file calling this function."""
    try:
        path = os.path.abspath(path)
        path = os.path.dirname(path)
        path = os.path.join(path, "nostr-metadata.yml")
        if not os.path.exists(path):
            return None
    except Exception as e:
        logger.info(f"Failed to find default metadata file: {e}")
        return None
    return path


def metadata_from_yaml(path: str) -> Metadata | None:
    """Utility function to convert a metadata file to a Metadata object. By default, it will look for a file named 'nostr-metadata.yml' in the same directory as the file calling this function."""
    if path is None:
        return None
    if not path.endswith('.yml') and not path.endswith('.yaml'):
        # Checking for default metadata file
        path = default_metadata_file(path)
    if path is not None and os.path.exists(path):
        logger.info(f"Loading metadata from {path}")
        with open(path, 'r') as f:
            metadata = yaml.safe_load(f)
            # Remove keys of empty values
            metadata = {k: v for k, v in metadata.items() if v}
            return Metadata(**metadata)
    else:
        logger.debug(f"Metadata file {path} does not exist")
        return None


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