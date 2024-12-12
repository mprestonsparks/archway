"""
Tests for {provider_name} provider.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.providers.{provider_lowercase} import {provider_name}Provider, {provider_name}Config
from src.types import CodeContext, AnalysisResult, RefactoringResult, ArchitectureResult


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = AsyncMock()
    client.analyze = AsyncMock(return_value="analysis_result")
    client.suggest_refactoring = AsyncMock(return_value="refactoring_result")
    client.explain_architecture = AsyncMock(return_value="architecture_result")
    client.close = AsyncMock()
    return client


@pytest.fixture
def provider():
    """Create a provider instance."""
    return {provider_name}Provider()


@pytest.mark.asyncio
async def test_provider_initialization(provider, monkeypatch):
    """Test provider initialization."""
    # Mock _setup_client
    mock_setup = AsyncMock(return_value=AsyncMock())
    monkeypatch.setattr(provider, "_setup_client", mock_setup)
    
    # Initialize
    await provider.initialize()
    
    # Assert
    assert provider._initialized
    mock_setup.assert_called_once()


@pytest.mark.asyncio
async def test_provider_analyze_code(provider, mock_client, monkeypatch):
    """Test code analysis."""
    # Setup
    monkeypatch.setattr(provider, "_client", mock_client)
    provider._initialized = True
    context = CodeContext(code="test code")
    
    # Execute
    result = await provider.analyze_code(context)
    
    # Assert
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.analysis == "analysis_result"
    mock_client.analyze.assert_called_once_with("test code")


@pytest.mark.asyncio
async def test_provider_suggest_refactoring(provider, mock_client, monkeypatch):
    """Test refactoring suggestions."""
    # Setup
    monkeypatch.setattr(provider, "_client", mock_client)
    provider._initialized = True
    context = CodeContext(code="test code")
    
    # Execute
    result = await provider.suggest_refactoring(context)
    
    # Assert
    assert isinstance(result, RefactoringResult)
    assert result.success
    assert result.suggestions == "refactoring_result"
    mock_client.suggest_refactoring.assert_called_once_with("test code")


@pytest.mark.asyncio
async def test_provider_explain_architecture(provider, mock_client, monkeypatch):
    """Test architecture explanation."""
    # Setup
    monkeypatch.setattr(provider, "_client", mock_client)
    provider._initialized = True
    context = CodeContext(code="test code")
    
    # Execute
    result = await provider.explain_architecture(context)
    
    # Assert
    assert isinstance(result, ArchitectureResult)
    assert result.success
    assert result.explanation == "architecture_result"
    mock_client.explain_architecture.assert_called_once_with("test code")


@pytest.mark.asyncio
async def test_provider_cleanup(provider, mock_client, monkeypatch):
    """Test provider cleanup."""
    # Setup
    monkeypatch.setattr(provider, "_client", mock_client)
    provider._initialized = True
    
    # Execute
    await provider.cleanup()
    
    # Assert
    assert not provider._initialized
    assert provider._client is None
    mock_client.close.assert_called_once()


def test_provider_config():
    """Test provider configuration."""
    config = {provider_name}Config(
        api_key="test_key",
        model="test_model",
        max_tokens=500,
        temperature=0.5
    )
    assert config.api_key == "test_key"
    assert config.model == "test_model"
    assert config.max_tokens == 500
    assert config.temperature == 0.5
    assert isinstance(config.additional_params, dict)
