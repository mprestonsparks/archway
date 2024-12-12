"""Code indexing adapter module."""

import json
from dataclasses import dataclass
from typing import List, Optional

import requests

from ..ports.indexing import (
    CodeDefinition,
    CodeLocation,
    CodeReference,
    IndexConfig,
    IndexProvider,
    SearchResult,
)


@dataclass
class SourcegraphConfig(IndexConfig):
    """Configuration for Sourcegraph indexer."""

    endpoint: str
    token: str


class SourcegraphIndexer(IndexProvider):
    """Provider for Sourcegraph code indexing."""

    def __init__(self, config: SourcegraphConfig):
        """Initialize the Sourcegraph indexer.

        Args:
            config: Sourcegraph configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {config.token}",
                "Content-Type": "application/json",
            }
        )

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for code using Sourcegraph.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        url = f"{self.config.endpoint}/api/search/stream"
        params = {
            "q": query,
            "limit": limit,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        results = []
        for line in response.text.strip().split("\n"):
            if not line:
                continue
            data = json.loads(line)
            if "type" not in data or data["type"] != "match":
                continue

            match = data["data"]
            results.append(
                SearchResult(
                    path=match["path"],
                    repository=match["repository"],
                    content=match["content"],
                    line_number=match["line"],
                )
            )

        return results

    async def get_definition(self, location: CodeLocation) -> Optional[CodeDefinition]:
        """Get the definition of a symbol.

        Args:
            location: Location of the symbol

        Returns:
            Definition of the symbol if found
        """
        url = f"{self.config.endpoint}/api/definitions"
        params = {
            "path": location.path,
            "line": location.line,
            "character": location.character,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if not data["definitions"]:
            return None

        definition = data["definitions"][0]
        return CodeDefinition(
            path=definition["path"],
            repository=definition["repository"],
            line=definition["line"],
            character=definition["character"],
            content=definition["content"],
        )

    async def get_references(self, location: CodeLocation) -> List[CodeReference]:
        """Get references to a symbol.

        Args:
            location: Location of the symbol

        Returns:
            List of references to the symbol
        """
        url = f"{self.config.endpoint}/api/references"
        params = {
            "path": location.path,
            "line": location.line,
            "character": location.character,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        references = []
        for ref in data["references"]:
            references.append(
                CodeReference(
                    path=ref["path"],
                    repository=ref["repository"],
                    line=ref["line"],
                    character=ref["character"],
                    content=ref["content"],
                )
            )

        return references
