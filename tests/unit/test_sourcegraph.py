"""Unit tests for Sourcegraph adapter."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.adapters.indexing.sourcegraph import SourcegraphConfig, SourcegraphIndexer
from src.core.models import CodeLocation, CodeSnippet

@pytest.fixture
def config():
    """Create a test configuration."""
    return SourcegraphConfig(
        endpoint_url="http://test-sourcegraph:7080",
        api_token="test-token"
    )

@pytest.fixture
async def indexer(config):
    """Create a test indexer instance."""
    indexer = SourcegraphIndexer(config)
    yield indexer
    await indexer.close()

@pytest.fixture
def mock_repository_response():
    """Create a mock repository response."""
    return {
        "data": {
            "repository": {
                "defaultBranch": {
                    "target": {
                        "commit": {
                            "blob": {
                                "lsif": {
                                    "diagnostics": {
                                        "totalCount": 10
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

@pytest.fixture
def mock_stats_response():
    """Create a mock stats response."""
    return {
        "data": {
            "repository": {
                "commit": {
                    "tree": {
                        "entries": [
                            {
                                "path": "test.py",
                                "isDirectory": False,
                                "languageId": "python"
                            },
                            {
                                "path": "src",
                                "isDirectory": True,
                                "languageId": None
                            }
                        ]
                    }
                }
            }
        }
    }

@pytest.mark.asyncio
async def test_initialization_success(indexer):
    """Test successful initialization."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(status_code=200)
        result = await indexer.initialize()
        assert result is True
        assert indexer._initialized is True

@pytest.mark.asyncio
async def test_initialization_failure(indexer):
    """Test failed initialization."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")
        result = await indexer.initialize()
        assert result is False
        assert indexer._initialized is False

@pytest.mark.asyncio
async def test_index_codebase(
    indexer,
    mock_repository_response,
    mock_stats_response
):
    """Test indexing a codebase."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = [
            AsyncMock(
                status_code=200,
                json=lambda: mock_repository_response
            ),
            AsyncMock(
                status_code=200,
                json=lambda: mock_stats_response
            )
        ]
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await indexer.initialize()
        
        result = await indexer.index_codebase("test-repo")
        
        assert result.root_path == "test-repo"
        assert len(result.indexed_files) == 1
        assert result.total_files == 1
        assert result.languages == {"python": 1}

@pytest.mark.asyncio
async def test_search(indexer):
    """Test searching for code."""
    mock_search_response = {
        "data": {
            "search": {
                "results": {
                    "matchCount": 1,
                    "results": [
                        {
                            "file": {
                                "path": "test.py",
                                "content": "def test(): pass",
                                "commit": {
                                    "oid": "123",
                                    "author": {
                                        "date": "2024-01-01T00:00:00"
                                    }
                                }
                            },
                            "lineMatches": [
                                {
                                    "lineNumber": 1,
                                    "offsetAndLengths": [[0, 4]],
                                    "preview": "def test(): pass"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_search_response
        )
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await indexer.initialize()
        
        results = await indexer.search("test")
        
        assert len(results) == 1
        assert results[0].content == "def test(): pass"
        assert results[0].location.file_path == "test.py"
        assert results[0].language == "python"

@pytest.mark.asyncio
async def test_get_context(indexer):
    """Test getting context for a snippet."""
    mock_context_response = {
        "data": {
            "repository": {
                "commit": {
                    "blob": {
                        "content": "def test():\n    pass\n",
                        "lsif": {
                            "hover": {
                                "markdown": {
                                    "text": "Test function"
                                }
                            },
                            "definitions": {
                                "nodes": [
                                    {
                                        "resource": {
                                            "path": "test.py",
                                            "repository": {
                                                "name": "test-repo"
                                            }
                                        },
                                        "range": {
                                            "start": {
                                                "line": 1
                                            },
                                            "end": {
                                                "line": 2
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
    
    snippet = CodeSnippet(
        content="def test(): pass",
        location=CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=1
        ),
        language="python",
        last_modified=datetime.utcnow()
    )
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_context_response
        )
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await indexer.initialize()
        
        results = await indexer.get_context(snippet)
        
        assert len(results) > 0
        assert any(r.language == "markdown" for r in results)  # Hover info
        assert any(r.language == "python" for r in results)  # Definition

@pytest.mark.asyncio
async def test_error_handling(indexer):
    """Test error handling in various operations."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.RequestError("API error")
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await indexer.initialize()
        
        with pytest.raises(RuntimeError):
            await indexer.index_codebase("test-repo")
        
        with pytest.raises(RuntimeError):
            await indexer.search("test")
        
        snippet = CodeSnippet(
            content="test",
            location=CodeLocation(
                file_path="test.py",
                start_line=1
            ),
            language="python",
            last_modified=datetime.utcnow()
        )
        with pytest.raises(RuntimeError):
            await indexer.get_context(snippet)
