"""Code indexing port interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IndexConfig:
    """Base configuration for index providers."""

    pass


@dataclass
class SearchResult:
    """Result from a code search."""

    path: str
    repository: str
    content: str
    line_number: int


@dataclass
class CodeLocation:
    """Location of a code symbol."""

    path: str
    line: int
    character: int


@dataclass
class CodeDefinition:
    """Definition of a code symbol."""

    path: str
    repository: str
    line: int
    character: int
    content: str


@dataclass
class CodeReference:
    """Reference to a code symbol."""

    path: str
    repository: str
    line: int
    character: int
    content: str


class IndexProvider(ABC):
    """Base class for code indexing providers."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for code.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def get_definition(self, location: CodeLocation) -> Optional[CodeDefinition]:
        """Get the definition of a symbol.

        Args:
            location: Location of the symbol

        Returns:
            Definition of the symbol if found
        """
        pass

    @abstractmethod
    async def get_references(self, location: CodeLocation) -> List[CodeReference]:
        """Get references to a symbol.

        Args:
            location: Location of the symbol

        Returns:
            List of references to the symbol
        """
        pass
