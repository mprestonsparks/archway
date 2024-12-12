"""Integration tests for Sourcegraph adapter."""
import os
from typing import AsyncGenerator

import pytest

from src.adapters.indexing import SourcegraphConfig, SourcegraphIndexer


@pytest.fixture
async def sourcegraph_indexer() -> AsyncGenerator[SourcegraphIndexer, None]:
    """Create and initialize a Sourcegraph indexer."""
    endpoint = os.getenv("SOURCEGRAPH_ENDPOINT")
    token = os.getenv("SOURCEGRAPH_TOKEN")
    if not endpoint or not token:
        pytest.skip("Sourcegraph credentials not found in environment")
    
    config = SourcegraphConfig(
        endpoint=endpoint,
        token=token
    )
    indexer = SourcegraphIndexer(config)
    
    try:
        success = await indexer.initialize()
        if not success:
            pytest.skip("Failed to initialize Sourcegraph indexer")
        yield indexer
    finally:
        await indexer.close()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_index_repository(sourcegraph_indexer: SourcegraphIndexer):
    """Test indexing a repository."""
    repo_url = "https://github.com/example/test-repo"
    result = await sourcegraph_indexer.index_repository(repo_url)
    
    assert result
    assert isinstance(result, bool)
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_code(sourcegraph_indexer: SourcegraphIndexer):
    """Test searching for code."""
    query = "class UserService"
    results = await sourcegraph_indexer.search(query)
    
    assert results
    assert isinstance(results, list)
    assert len(results) > 0
    assert all("UserService" in result.content for result in results)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_definition(sourcegraph_indexer: SourcegraphIndexer):
    """Test getting code definition."""
    file_path = "src/services/user_service.py"
    line = 10
    character = 15
    
    result = await sourcegraph_indexer.get_definition(
        file_path=file_path,
        line=line,
        character=character
    )
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_references(sourcegraph_indexer: SourcegraphIndexer):
    """Test getting code references."""
    file_path = "src/services/user_service.py"
    line = 10
    character = 15
    
    results = await sourcegraph_indexer.get_references(
        file_path=file_path,
        line=line,
        character=character
    )
    
    assert results
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_hover(sourcegraph_indexer: SourcegraphIndexer):
    """Test getting hover information."""
    file_path = "src/services/user_service.py"
    line = 10
    character = 15
    
    result = await sourcegraph_indexer.get_hover(
        file_path=file_path,
        line=line,
        character=character
    )
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0
