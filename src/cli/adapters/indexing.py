"""Sourcegraph adapter for code indexing."""
from dataclasses import dataclass
from typing import List, Optional

import requests


@dataclass
class SourcegraphConfig:
    """Configuration for Sourcegraph indexer."""
    endpoint: str
    token: str


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


class SourcegraphIndexer:
    """Sourcegraph indexer."""
    def __init__(self, config: SourcegraphConfig):
        """Initialize Sourcegraph indexer."""
        self.config = config
        self.headers = {
            "Authorization": f"token {config.token}",
            "Content-Type": "application/json",
        }

    def search(self, query: str) -> List[CodeSnippet]:
        """Search code using Sourcegraph."""
        url = f"{self.config.endpoint}/api/search/stream"
        params = {"q": query}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        results = []
        for line in response.text.splitlines():
            if not line:
                continue
            data = response.json()
            for result in data.get("matches", []):
                location = CodeLocation(
                    file=result["file"]["path"],
                    line=result["lineNumber"],
                    character=result["offsetAndLength"][0],
                )
                snippet = CodeSnippet(
                    content=result["content"],
                    location=location,
                )
                results.append(snippet)

        return results

    def get_definition(self, location: CodeLocation) -> Optional[CodeLocation]:
        """Get definition of a symbol."""
        url = f"{self.config.endpoint}/api/definitions"
        params = {
            "file": location.file,
            "line": location.line,
            "character": location.character,
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        if not data.get("locations"):
            return None

        result = data["locations"][0]
        return CodeLocation(
            file=result["file"],
            line=result["line"],
            character=result["character"],
        )

    def get_references(self, location: CodeLocation) -> List[CodeLocation]:
        """Get references to a symbol."""
        url = f"{self.config.endpoint}/api/references"
        params = {
            "file": location.file,
            "line": location.line,
            "character": location.character,
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        results = []
        for result in data.get("locations", []):
            location = CodeLocation(
                file=result["file"],
                line=result["line"],
                character=result["character"],
            )
            results.append(location)

        return results
