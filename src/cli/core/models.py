"""Core models for Archway."""
from dataclasses import dataclass


@dataclass
class CodeLocation:
    """Location in code."""
    file: str
    line: int
    character: int


@dataclass
class CodeSnippet:
    """Code snippet."""
    content: str
    location: CodeLocation
