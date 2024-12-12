"""
Tests for {command_name} command.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.cli.commands.{command_lowercase} import {command_name}Command, {command_name}Config
from src.cli.base import Context, Result
from src.adapters.llm import BaseProvider


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = AsyncMock(spec=BaseProvider)
    provider.initialize = AsyncMock()
    provider.close = AsyncMock()
    provider.some_method = AsyncMock(return_value="test_result")
    return provider


@pytest.fixture
def command():
    """Create a command instance."""
    return {command_name}Command()


@pytest.mark.asyncio
async def test_command_initialization(command, mock_provider):
    """Test command initialization."""
    await command.initialize(mock_provider)
    mock_provider.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_command_execution_success(command, mock_provider):
    """Test successful command execution."""
    # Setup
    await command.initialize(mock_provider)
    context = Context(args=MagicMock())
    
    # Execute
    result = await command.execute(context)
    
    # Assert
    assert isinstance(result, Result)
    assert result.success
    assert result.data == "test_result"
    mock_provider.some_method.assert_called_once()


@pytest.mark.asyncio
async def test_command_execution_failure(command, mock_provider):
    """Test command execution failure."""
    # Setup
    await command.initialize(mock_provider)
    mock_provider.some_method.side_effect = Exception("Test error")
    context = Context(args=MagicMock())
    
    # Execute
    result = await command.execute(context)
    
    # Assert
    assert isinstance(result, Result)
    assert not result.success
    assert "Test error" in result.error


@pytest.mark.asyncio
async def test_command_cleanup(command, mock_provider):
    """Test command cleanup."""
    # Setup
    await command.initialize(mock_provider)
    
    # Execute
    await command.cleanup()
    
    # Assert
    mock_provider.close.assert_called_once()


def test_command_config():
    """Test command configuration."""
    config = {command_name}Config()
    assert config.name == "{command_lowercase}"
    assert len(config.options) > 0
