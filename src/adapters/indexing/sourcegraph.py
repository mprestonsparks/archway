"""Sourcegraph adapter implementation for code indexing and search."""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field

from src.core.models import CodeLocation, CodeSnippet, CodebaseContext
from src.ports.code_analysis import CodeIndexer


class SourcegraphConfig(BaseModel):
    """Configuration for Sourcegraph integration."""
    endpoint_url: str = Field(default="http://localhost:7080")
    api_token: str = Field(default=None)
    timeout: float = Field(default=30.0)
    batch_size: int = Field(default=50)
    max_retries: int = Field(default=3)


class SourcegraphIndexer(CodeIndexer):
    """Adapter for Sourcegraph code indexing and search."""

    def __init__(self, config: Optional[SourcegraphConfig] = None):
        """Initialize the Sourcegraph indexer."""
        self.config = config or SourcegraphConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the connection to Sourcegraph."""
        try:
            headers = self._get_headers()
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=headers,
                base_url=self.config.endpoint_url
            )
            # Test connection
            await self._client.get("/.api/graphql")
            self._initialized = True
            return True
        except httpx.RequestError:
            self._initialized = False
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Sourcegraph API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.config.api_token:
            headers["Authorization"] = f"token {self.config.api_token}"
        return headers

    async def _ensure_initialized(self) -> None:
        """Ensure the indexer is initialized."""
        if not self._initialized:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize Sourcegraph indexer")

    async def index_codebase(self, root_path: str) -> CodebaseContext:
        """Index the codebase using Sourcegraph."""
        await self._ensure_initialized()

        try:
            # Get repository information
            query = """
            query ($path: String!) {
              repository(name: $path) {
                defaultBranch {
                  target {
                    commit {
                      blob {
                        lsif {
                          diagnostics {
                            totalCount
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            variables = {"path": root_path}
            response = await self._client.post(
                "/.api/graphql",
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            # Get file statistics
            stats_query = """
            query ($path: String!) {
              repository(name: $path) {
                commit(rev: "HEAD") {
                  tree {
                    entries {
                      path
                      isDirectory
                      languageId
                    }
                  }
                }
              }
            }
            """
            stats_response = await self._client.post(
                "/.api/graphql",
                json={"query": stats_query, "variables": variables}
            )
            stats_response.raise_for_status()
            stats_data = stats_response.json()

            # Process file statistics
            files = stats_data["data"]["repository"]["commit"]["tree"]["entries"]
            indexed_files = [f["path"] for f in files if not f["isDirectory"]]
            languages = {}
            for f in files:
                if not f["isDirectory"] and f["languageId"]:
                    languages[f["languageId"]] = languages.get(f["languageId"], 0) + 1

            return CodebaseContext(
                root_path=root_path,
                indexed_files=indexed_files,
                last_indexed=datetime.utcnow(),
                total_files=len(indexed_files),
                languages=languages
            )

        except (httpx.RequestError, KeyError) as e:
            raise RuntimeError(f"Failed to index codebase: {str(e)}")

    async def search(self, query: str) -> List[CodeSnippet]:
        """Search for code snippets using Sourcegraph."""
        await self._ensure_initialized()

        try:
            search_query = """
            query ($searchQuery: String!) {
              search(query: $searchQuery) {
                results {
                  matchCount
                  results {
                    ... on FileMatch {
                      file {
                        path
                        content
                        commit {
                          oid
                          author {
                            date
                          }
                        }
                      }
                      lineMatches {
                        lineNumber
                        offsetAndLengths
                        preview
                      }
                    }
                  }
                }
              }
            }
            """
            variables = {"searchQuery": query}
            response = await self._client.post(
                "/.api/graphql",
                json={"query": search_query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            snippets = []
            for result in data["data"]["search"]["results"]["results"]:
                file_path = result["file"]["path"]
                content = result["file"]["content"]
                last_modified = datetime.fromisoformat(
                    result["file"]["commit"]["author"]["date"].rstrip("Z")
                )

                for match in result["lineMatches"]:
                    line_number = match["lineNumber"]
                    preview = match["preview"]
                    snippets.append(
                        CodeSnippet(
                            content=preview,
                            location=CodeLocation(
                                file_path=file_path,
                                start_line=line_number,
                                end_line=line_number
                            ),
                            language=self._detect_language(file_path),
                            last_modified=last_modified
                        )
                    )

            return snippets

        except (httpx.RequestError, KeyError) as e:
            raise RuntimeError(f"Search failed: {str(e)}")

    async def get_context(self, snippet: CodeSnippet) -> List[CodeSnippet]:
        """Get surrounding context for a code snippet."""
        await self._ensure_initialized()

        try:
            query = """
            query ($path: String!, $line: Int!) {
              repository {
                commit(rev: "HEAD") {
                  blob(path: $path) {
                    content
                    lsif {
                      hover(line: $line, character: 0) {
                        markdown {
                          text
                        }
                      }
                      definitions(line: $line, character: 0) {
                        nodes {
                          resource {
                            path
                            repository {
                              name
                            }
                          }
                          range {
                            start {
                              line
                            }
                            end {
                              line
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            variables = {
                "path": snippet.location.file_path,
                "line": snippet.location.start_line
            }
            response = await self._client.post(
                "/.api/graphql",
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            context_snippets = []
            
            # Add hover information if available
            hover_data = data["data"]["repository"]["commit"]["blob"]["lsif"]["hover"]
            if hover_data and hover_data["markdown"]:
                context_snippets.append(
                    CodeSnippet(
                        content=hover_data["markdown"]["text"],
                        location=CodeLocation(
                            file_path=snippet.location.file_path,
                            start_line=snippet.location.start_line - 1
                        ),
                        language="markdown",
                        last_modified=snippet.last_modified
                    )
                )

            # Add definition locations
            for def_node in data["data"]["repository"]["commit"]["blob"]["lsif"]["definitions"]["nodes"]:
                def_path = def_node["resource"]["path"]
                def_start = def_node["range"]["start"]["line"]
                def_end = def_node["range"]["end"]["line"]

                # Fetch the definition content
                def_content = await self._fetch_file_content(def_path, def_start, def_end)
                if def_content:
                    context_snippets.append(
                        CodeSnippet(
                            content=def_content,
                            location=CodeLocation(
                                file_path=def_path,
                                start_line=def_start,
                                end_line=def_end
                            ),
                            language=self._detect_language(def_path),
                            last_modified=snippet.last_modified
                        )
                    )

            return context_snippets

        except (httpx.RequestError, KeyError) as e:
            raise RuntimeError(f"Failed to get context: {str(e)}")

    async def _fetch_file_content(
        self,
        file_path: str,
        start_line: int,
        end_line: int
    ) -> Optional[str]:
        """Fetch content for a specific file range."""
        try:
            query = """
            query ($path: String!) {
              repository {
                commit(rev: "HEAD") {
                  blob(path: $path) {
                    content
                  }
                }
              }
            }
            """
            variables = {"path": file_path}
            response = await self._client.post(
                "/.api/graphql",
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()

            content = data["data"]["repository"]["commit"]["blob"]["content"]
            lines = content.splitlines()
            return "\n".join(lines[start_line - 1:end_line])

        except (httpx.RequestError, KeyError, IndexError):
            return None

    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".sh": "shell",
            ".yaml": "yaml",
            ".json": "json",
        }
        
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        return "text"

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._initialized = False
