"""Tests for OpenAI o1 model adapter."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.adapters.llm.o1_model import O1Config, O1ModelProvider
from src.core.models import CodeLocation, CodeSnippet


@pytest.fixture
def code_snippet():
    """Create a test code snippet."""
    return CodeSnippet(
        content="def test_function():\n    return 'test'",
        language="python",
        location=CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=2
        )
    )


@pytest.fixture
def mock_openai():
    """Create a mock OpenAI client."""
    with patch("src.adapters.llm.o1_model.AsyncOpenAI") as mock:
        mock_client = AsyncMock()
        mock_client.models.retrieve = AsyncMock()
        mock_client.chat.completions.create = AsyncMock()
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def o1_provider():
    """Create an o1 model provider with test config."""
    config = O1Config(api_key="test_key")
    return O1ModelProvider(config)


@pytest.mark.asyncio
async def test_initialize_success(o1_provider, mock_openai):
    """Test successful initialization."""
    result = await o1_provider.initialize()
    assert result is True
    assert o1_provider._initialized is True
    mock_openai.assert_called_once_with(api_key="test_key")


@pytest.mark.asyncio
async def test_initialize_failure(o1_provider, mock_openai):
    """Test initialization failure."""
    mock_openai.side_effect = Exception("API Error")
    result = await o1_provider.initialize()
    assert result is False
    assert o1_provider._initialized is False


@pytest.mark.asyncio
async def test_initialize_no_api_key():
    """Test initialization with no API key."""
    provider = O1ModelProvider(O1Config())
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        await provider.initialize()


@pytest.mark.asyncio
async def test_generate_success(o1_provider, mock_openai, code_snippet):
    """Test successful generation."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    o1_provider._client.chat.completions.create.return_value = mock_response
    
    await o1_provider.initialize()
    result = await o1_provider.generate(
        "Test prompt",
        code_snippets=[code_snippet]
    )
    
    assert result == "Test response"
    o1_provider._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_failure(o1_provider, mock_openai):
    """Test generation failure."""
    o1_provider._client.chat.completions.create.side_effect = Exception("API Error")
    
    await o1_provider.initialize()
    with pytest.raises(RuntimeError, match="Error generating response"):
        await o1_provider.generate("Test prompt")


@pytest.mark.asyncio
async def test_stream_generate(o1_provider, mock_openai):
    """Test streaming generation."""
    async def mock_stream():
        chunks = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" World"))])
        ]
        for chunk in chunks:
            yield chunk

    o1_provider._client.chat.completions.create.return_value = mock_stream()
    
    await o1_provider.initialize()
    chunks = []
    async for chunk in await o1_provider.stream_generate("Test prompt"):
        chunks.append(chunk)
    
    assert chunks == ["Hello", " World"]


@pytest.mark.asyncio
async def test_analyze_code(o1_provider, mock_openai, code_snippet):
    """Test code analysis."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Analysis result"
    o1_provider._client.chat.completions.create.return_value = mock_response
    
    await o1_provider.initialize()
    result = await o1_provider.analyze_code(
        code_snippet,
        analysis_type="security"
    )
    
    assert result == "Analysis result"
    o1_provider._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_suggest_refactoring(o1_provider, mock_openai, code_snippet):
    """Test refactoring suggestions."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Refactoring suggestions"
    o1_provider._client.chat.completions.create.return_value = mock_response
    
    await o1_provider.initialize()
    result = await o1_provider.suggest_refactoring(
        code_snippet,
        goal="Improve performance"
    )
    
    assert result == "Refactoring suggestions"
    o1_provider._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_explain_architecture(o1_provider, mock_openai, code_snippet):
    """Test architecture explanation."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Architecture explanation"
    o1_provider._client.chat.completions.create.return_value = mock_response
    
    await o1_provider.initialize()
    result = await o1_provider.explain_architecture([code_snippet])
    
    assert result == "Architecture explanation"
    o1_provider._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_close(o1_provider, mock_openai):
    """Test provider cleanup."""
    await o1_provider.initialize()
    await o1_provider.close()
    
    assert o1_provider._initialized is False
    o1_provider._client.close.assert_called_once()
