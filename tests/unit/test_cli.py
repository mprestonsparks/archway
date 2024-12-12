"""Tests for Archway CLI."""
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from src.cli.commands import cli
from src.core.models import CodeLocation, CodeSnippet


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_o1_provider():
    """Mock the o1 model provider."""
    with patch("src.cli.commands.O1ModelProvider") as mock:
        provider = AsyncMock()
        provider.initialize = AsyncMock(return_value=True)
        provider.close = AsyncMock()
        provider.analyze_code = AsyncMock(return_value="Analysis result")
        provider.suggest_refactoring = AsyncMock(return_value="Refactoring suggestions")
        provider.explain_architecture = AsyncMock(return_value="Architecture explanation")
        mock.return_value = provider
        yield provider


@pytest.fixture
def mock_sourcegraph_indexer():
    """Mock the Sourcegraph indexer."""
    with patch("src.cli.commands.SourcegraphIndexer") as mock:
        indexer = AsyncMock()
        indexer.initialize = AsyncMock(return_value=True)
        indexer.close = AsyncMock()
        indexer.search = AsyncMock(return_value=[
            CodeSnippet(
                content="def test():\n    pass",
                language="python",
                location=CodeLocation(
                    path="test.py",
                    line=1,
                    character=0
                )
            )
        ])
        indexer.get_definition = AsyncMock(return_value="Test definition")
        indexer.get_references = AsyncMock(return_value=[
            CodeSnippet(
                content="test()",
                language="python",
                location=CodeLocation(
                    path="main.py",
                    line=10,
                    character=0
                )
            )
        ])
        mock.return_value = indexer
        yield indexer


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Archway CLI" in result.output


def test_analyze_help(runner):
    """Test analyze help command."""
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "Analyze code" in result.output


def test_search_help(runner):
    """Test search help command."""
    result = runner.invoke(cli, ["search", "--help"])
    assert result.exit_code == 0
    assert "Search code" in result.output


def test_analyze_code_no_api_key(runner, tmp_path):
    """Test analyze code command without API key."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        result = runner.invoke(cli, ["analyze", "code", str(test_file)])
        assert result.exit_code == 1
        assert "OpenAI API key not found in environment" in result.output


def test_analyze_code_success(runner, tmp_path, mock_o1_provider):
    """Test analyze code command."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = runner.invoke(cli, ["analyze", "code", str(test_file)])
    
    assert result.exit_code == 0
    assert "Analysis result" in result.output
    mock_o1_provider.analyze_code.assert_called_once()


def test_analyze_refactor_success(runner, tmp_path, mock_o1_provider):
    """Test analyze refactor command."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = runner.invoke(cli, [
            "analyze", "refactor",
            str(test_file),
            "--goal", "improve performance"
        ])
    
    assert result.exit_code == 0
    assert "Refactoring suggestions" in result.output
    mock_o1_provider.suggest_refactoring.assert_called_once()


def test_analyze_architecture_success(runner, tmp_path, mock_o1_provider):
    """Test analyze architecture command."""
    test_files = []
    for i in range(2):
        file = tmp_path / f"test{i}.py"
        file.write_text("def test():\n    pass")
        test_files.append(str(file))
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = runner.invoke(cli, ["analyze", "architecture"] + test_files)
    
    assert result.exit_code == 0
    assert "Architecture explanation" in result.output
    mock_o1_provider.explain_architecture.assert_called_once()


def test_search_code_success(runner, mock_sourcegraph_indexer):
    """Test search code command."""
    with patch.dict(os.environ, {
        "SOURCEGRAPH_ENDPOINT": "http://test",
        "SOURCEGRAPH_TOKEN": "test_token"
    }):
        result = runner.invoke(cli, ["search", "code", "test"])
    
    assert result.exit_code == 0
    assert "test.py" in result.output
    mock_sourcegraph_indexer.search.assert_called_once_with("test")


def test_search_definition_success(runner, tmp_path, mock_sourcegraph_indexer):
    """Test search definition command."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")
    
    with patch.dict(os.environ, {
        "SOURCEGRAPH_ENDPOINT": "http://test",
        "SOURCEGRAPH_TOKEN": "test_token"
    }):
        result = runner.invoke(cli, [
            "search", "definition",
            str(test_file),
            "--line", "1",
            "--character", "5"
        ])
    
    assert result.exit_code == 0
    assert "Test definition" in result.output
    mock_sourcegraph_indexer.get_definition.assert_called_once()


def test_search_references_success(runner, tmp_path, mock_sourcegraph_indexer):
    """Test search references command."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")
    
    with patch.dict(os.environ, {
        "SOURCEGRAPH_ENDPOINT": "http://test",
        "SOURCEGRAPH_TOKEN": "test_token"
    }):
        result = runner.invoke(cli, [
            "search", "references",
            str(test_file),
            "--line", "1",
            "--character", "5"
        ])
    
    assert result.exit_code == 0
    assert "main.py" in result.output
    mock_sourcegraph_indexer.get_references.assert_called_once()
