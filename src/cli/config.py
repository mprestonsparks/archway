"""Configuration utilities for the CLI."""
import os
from typing import Optional

from dotenv import load_dotenv


def load_config() -> None:
    """Load configuration from environment variables."""
    load_dotenv()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Value of the environment variable or default
    """
    return os.getenv(key, default)
