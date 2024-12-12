"""Archway CLI commands for code analysis and search.

This module provides a command-line interface for:
1. Code Analysis:
   - Analyze single files for insights and improvements
   - Get refactoring suggestions based on specific goals
   - Analyze architecture across multiple files

2. Code Search:
   - Search code using Sourcegraph integration
   - Find symbol definitions and references
   - Navigate code semantically

3. Storage:
   - Store and manage analysis history

Environment Variables:
    OPENAI_API_KEY: Required for LLM-based code analysis
    SOURCEGRAPH_ENDPOINT: Required for code search and navigation
    SOURCEGRAPH_TOKEN: Required for Sourcegraph authentication

Example Usage:
    # Analyze a file
    $ archway analyze code path/to/file.py

    # Get refactoring suggestions
    $ archway analyze refactor path/to/file.py "improve performance"

    # Search code
    $ archway search search-code "function definition"

    # Show analysis history
    $ archway history list
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar

import click
from dotenv import load_dotenv

# Type ignore for missing stubs
from ports.indexing import CodeLocation, IndexProvider  # type: ignore
from ports.llm import LLMProvider  # type: ignore
from ports.storage import StorageProvider, AnalysisResult, AnalysisType  # type: ignore
from src.adapters.indexing import SourcegraphConfig, SourcegraphIndexer
from src.adapters.llm import O1Config, O1ModelProvider
from src.adapters.storage import SQLiteConfig, SQLiteStorage

# Load environment variables
load_dotenv()

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

def get_llm_provider() -> LLMProvider:
    """Get an initialized LLM provider.
    
    Returns:
        LLMProvider: Initialized LLM provider instance
        
    Raises:
        click.ClickException: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise click.ClickException("OPENAI_API_KEY environment variable not set")
    config = O1Config(api_key=api_key)
    return O1ModelProvider(config)


def get_index_provider() -> IndexProvider:
    """Get an initialized index provider.
    
    Returns:
        IndexProvider: Initialized index provider instance
        
    Raises:
        click.ClickException: If required environment variables are not set
    """
    endpoint = os.getenv("SOURCEGRAPH_ENDPOINT")
    token = os.getenv("SOURCEGRAPH_TOKEN")
    if not endpoint or not token:
        raise click.ClickException(
            "SOURCEGRAPH_ENDPOINT and SOURCEGRAPH_TOKEN environment variables must be set"
        )
    config = SourcegraphConfig(endpoint=endpoint, token=token)
    return SourcegraphIndexer(config)


def get_storage_provider() -> StorageProvider:
    """Get an initialized storage provider."""
    config = SQLiteConfig()
    return SQLiteStorage(config)


def read_file(file_path: str) -> str:
    """Read a file and return its contents.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        str: Contents of the file
        
    Raises:
        click.ClickException: If file does not exist
    """
    path = Path(file_path)
    if not path.exists():
        raise click.ClickException(f"File {file_path} does not exist")
    return path.read_text()


def run_async(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run an async function in the event loop.
    
    Args:
        func: Async function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Any: Result of the async function
    """
    return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))


def wrap_async_command(cmd: F) -> F:
    """Wrap an async command to run in the event loop.
    
    Args:
        cmd: Command function to wrap
        
    Returns:
        F: Wrapped command function that runs in the event loop
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return run_async(cmd, *args, **kwargs)
    return wrapper  # type: ignore


@click.group()
def cli() -> None:
    """Archway CLI - AI-driven development environment."""


@cli.group()
def analyze() -> None:
    """Analyze code using AI models."""


@analyze.command()
@wrap_async_command
@click.argument("file_path", type=click.Path(exists=True))
def code(file_path: str) -> None:
    """Analyze code in a file.
    
    Args:
        file_path: Path to the file to analyze
    """
    provider = get_llm_provider()
    storage = get_storage_provider()
    content = read_file(file_path)

    async def _analyze() -> None:
        prompt = f"""Analyze the following code and provide insights:

{content}

Please include:
1. A brief overview of what the code does
2. Any potential issues or improvements
3. Best practices that could be applied
"""
        response = await provider.generate(prompt)
        result = AnalysisResult(
            analysis_type=AnalysisType.QUALITY,
            findings=[response.text],
            suggestions=[]
        )
        
        # Save the analysis
        record = await storage.save_analysis(file_path, result)
        
        click.echo(f"\nAnalysis saved with ID: {record.id}")
        click.echo(response.text)

    run_async(_analyze)


@analyze.command()
@wrap_async_command
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("goal")
def refactor(file_path: str, goal: str) -> None:
    """Get refactoring suggestions for code.
    
    Args:
        file_path: Path to the file to refactor
        goal: Refactoring goal description
    """
    provider = get_llm_provider()
    content = read_file(file_path)

    async def _analyze() -> str:
        prompt = f"""Analyze this code and suggest how to refactor it to achieve the following goal: {goal}

{content}

Please provide:
1. A clear explanation of the suggested changes
2. The benefits of these changes
3. Any potential risks or trade-offs
"""
        response = await provider.generate(prompt)
        return response.text

    result = run_async(_analyze)
    click.echo(result)


@analyze.command()
@wrap_async_command
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
def architecture(file_paths: List[str]) -> None:
    """Analyze the architecture of multiple files.
    
    Args:
        file_paths: List of paths to files to analyze
    """
    provider = get_llm_provider()
    contents = {path: read_file(path) for path in file_paths}

    async def _analyze() -> str:
        prompt = """Analyze the architecture of these files:

"""
        for path, content in contents.items():
            prompt += f"\n=== {path} ===\n{content}\n"

        prompt += """
Please provide:
1. An overview of the system architecture
2. The relationships between components
3. Any architectural improvements that could be made
"""
        response = await provider.generate(prompt)
        return response.text

    result = run_async(_analyze)
    click.echo(result)


@cli.group()
def search() -> None:
    """Search code using Sourcegraph."""


@search.command()
@wrap_async_command
@click.argument("query")
def search_code(query: str) -> None:
    """Search for code using Sourcegraph.
    
    Args:
        query: Search query string
    """
    indexer = get_index_provider()
    
    async def _search() -> None:
        results = await indexer.search(query)
        if not results:
            click.echo("No results found")
            return

        for result in results:
            click.echo(f"\n=== {result.path}:{result.line_number} ===")
            click.echo(result.content)

    run_async(_search)


@search.command()
@wrap_async_command
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("line", type=int)
@click.argument("character", type=int)
def definition(file_path: str, line: int, character: int) -> None:
    """Get the definition of a symbol.
    
    Args:
        file_path: Path to the file containing the symbol
        line: Line number of the symbol
        character: Character position of the symbol
    """
    indexer = get_index_provider()
    location = CodeLocation(path=file_path, line=line, character=character)
    
    async def _get_definition() -> None:
        result = await indexer.get_definition(location)
        if not result:
            click.echo("Definition not found")
            return

        click.echo(f"Definition found at {result.path}:{result.line}")
        click.echo(result.content)

    run_async(_get_definition)


@search.command()
@wrap_async_command
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("line", type=int)
@click.argument("character", type=int)
def references(file_path: str, line: int, character: int) -> None:
    """Get references to a symbol.
    
    Args:
        file_path: Path to the file containing the symbol
        line: Line number of the symbol
        character: Character position of the symbol
    """
    indexer = get_index_provider()
    location = CodeLocation(path=file_path, line=line, character=character)
    
    async def _get_references() -> None:
        results = await indexer.get_references(location)
        if not results:
            click.echo("No references found")
            return

        click.echo(f"Found {len(results)} references:")
        for result in results:
            click.echo(f"{result.path}:{result.line}")

    run_async(_get_references)


@cli.group()
def history() -> None:
    """Manage analysis history."""
    pass


@history.command()
@wrap_async_command
@click.argument("analysis_id")
def show(analysis_id: str) -> None:
    """Show a specific analysis result.
    
    Args:
        analysis_id: ID of the analysis to show
    """
    storage = get_storage_provider()
    
    async def _show() -> None:
        record = await storage.get_analysis(analysis_id)
        if not record:
            click.echo(f"Analysis {analysis_id} not found")
            return
            
        click.echo(f"\nAnalysis of {record.file_path}")
        click.echo(f"Timestamp: {record.timestamp}")
        click.echo("\nResults:")
        
        if isinstance(record.result, AnalysisResult):
            for finding in record.result.findings:
                click.echo(f"\n- {finding}")
            for suggestion in record.result.suggestions:
                click.echo(f"\nSuggestion: {suggestion}")
        else:
            click.echo(str(record.result))
    
    run_async(_show)


@history.command()
@wrap_async_command
@click.option("--file-path", help="Filter by file path")
@click.option("--since", help="Show analyses since date (YYYY-MM-DD)")
def list(file_path: Optional[str], since: Optional[str]) -> None:
    """List analysis history with optional filters.
    
    Args:
        file_path: Filter by file path
        since: Show analyses since date (YYYY-MM-DD)
    """
    storage = get_storage_provider()
    
    async def _list() -> None:
        start_date = None
        if since:
            try:
                start_date = datetime.strptime(since, "%Y-%m-%d")
            except ValueError:
                click.echo("Invalid date format. Use YYYY-MM-DD")
                return
        
        records = await storage.list_analyses(
            file_path=file_path,
            start_date=start_date
        )
        
        if not records:
            click.echo("No analyses found")
            return
            
        for record in records:
            click.echo(f"\nID: {record.id}")
            click.echo(f"File: {record.file_path}")
            click.echo(f"Date: {record.timestamp}")
            if isinstance(record.result, AnalysisResult):
                click.echo(f"Type: {record.result.analysis_type}")
    
    run_async(_list)


@history.command()
@wrap_async_command
@click.argument("analysis_id")
def delete(analysis_id: str) -> None:
    """Delete an analysis from history.
    
    Args:
        analysis_id: ID of the analysis to delete
    """
    storage = get_storage_provider()
    
    async def _delete() -> None:
        success = await storage.delete_analysis(analysis_id)
        if success:
            click.echo(f"Analysis {analysis_id} deleted")
        else:
            click.echo(f"Analysis {analysis_id} not found")
    
    run_async(_delete)
