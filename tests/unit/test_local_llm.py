"""Unit tests for local LLM adapter."""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from src.adapters.llm.local_llm import LocalLLMProvider, LLMConfig

@pytest.fixture
def config():
    """Create a test configuration."""
    return LLMConfig(
        endpoint_url="http://test-llm:8080/generate",
        max_new_tokens=100,
        temperature=0.5
    )

@pytest.fixture
async def provider(config):
    """Create a test provider instance."""
    provider = LocalLLMProvider(config)
    yield provider
    await provider.close()

@pytest.mark.asyncio
async def test_initialization_success(provider):
    """Test successful initialization."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(status_code=200)
        result = await provider.initialize()
        assert result is True
        assert provider._initialized is True

@pytest.mark.asyncio
async def test_initialization_failure(provider):
    """Test failed initialization."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed")
        result = await provider.initialize()
        assert result is False
        assert provider._initialized is False

@pytest.mark.asyncio
async def test_generate_success(provider):
    """Test successful generation."""
    test_response = {"generated_text": "Test response"}
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: test_response
        )
        
        # Initialize first
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await provider.initialize()
        
        response = await provider.generate("Test prompt")
        assert response == "Test response"

@pytest.mark.asyncio
async def test_generate_failure(provider):
    """Test generation failure."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.RequestError("Generation failed")
        
        # Initialize first
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await provider.initialize()
        
        with pytest.raises(RuntimeError):
            await provider.generate("Test prompt")

@pytest.mark.asyncio
async def test_stream_generate(provider):
    """Test streaming generation."""
    test_chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    
    async def mock_stream_response():
        for chunk in test_chunks:
            yield f"data: {chunk}\n"
        yield "data: [DONE]\n"
    
    mock_response = AsyncMock()
    mock_response.aiter_lines = mock_stream_response
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value.__aenter__.return_value = mock_response
        
        # Initialize first
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await provider.initialize()
        
        chunks = []
        async for chunk in provider.stream_generate("Test prompt"):
            chunks.append(chunk)
        
        assert chunks == test_chunks

@pytest.mark.asyncio
async def test_stream_generate_failure(provider):
    """Test streaming generation failure."""
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.RequestError("Streaming failed")
        
        # Initialize first
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = AsyncMock(status_code=200)
            await provider.initialize()
        
        with pytest.raises(RuntimeError):
            async for _ in provider.stream_generate("Test prompt"):
                pass
