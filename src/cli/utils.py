"""Utility functions for the CLI."""
import logging
from typing import Optional

from .config import get_env


def setup_logging(level: Optional[str] = None) -> None:
    """Set up logging configuration.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
    """
    if level is None:
        level = get_env("LOG_LEVEL", "info")
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
