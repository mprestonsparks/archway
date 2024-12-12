"""CLI commands for Archway."""
import asyncio
import os
from pathlib import Path
from typing import List, Optional

import click
from dotenv import load_dotenv

from src.adapters.llm import O1Config, O1ModelProvider
from src.adapters.indexing import SourcegraphConfig, SourcegraphIndexer
from src.core.models import CodeLocation, CodeSnippet


# Load environment variables
load_dotenv()


def get_o1_provider() -> O1ModelProvider:
    """Get an initialized o1 model provider."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise click.ClickException("OpenAI API key not found in environment. Please set OPENAI_API_KEY.")
    
    config = O1Config(
        api_key=api_key,
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
        model=os.getenv("OPENAI_MODEL", "gpt-4")
    )
    return O1ModelProvider(config)


def get_sourcegraph_indexer() -> SourcegraphIndexer:
    """Get an initialized Sourcegraph indexer."""
    endpoint = os.getenv("SOURCEGRAPH_ENDPOINT")
    token = os.getenv("SOURCEGRAPH_TOKEN")
    if not endpoint or not token:
        raise click.ClickException("Sourcegraph credentials not found in environment")
    
    config = SourcegraphConfig(endpoint=endpoint, token=token)
    return SourcegraphIndexer(config)


def read_file(file_path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        raise click.ClickException(f"Error reading file: {str(e)}")


@click.group()
def cli():
    """Archway CLI - AI-driven development environment."""
    pass


@cli.group()
def analyze():
    """Analyze code using AI models."""
    pass


@analyze.command()
@click.argument("file_path", type=click.Path(exists=True))
async def code(file_path: str):
    """Analyze code in a file."""
    content = read_file(file_path)
    snippet = CodeSnippet(
        content=content,
        language=Path(file_path).suffix[1:],  # Remove the dot
        location=CodeLocation(
            path=file_path,
            line=1,
            character=0
        )
    )
    
    provider = get_o1_provider()
    try:
        await provider.initialize()
        result = await provider.analyze_code(snippet)
        click.echo(result)
    finally:
        await provider.close()


@analyze.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--goal", "-g", required=True,
              help="Goal of the refactoring (e.g., improve performance)")
async def refactor(file_path: str, goal: str):
    """Get refactoring suggestions for code."""
    content = read_file(file_path)
    snippet = CodeSnippet(
        content=content,
        language=Path(file_path).suffix[1:],
        location=CodeLocation(
            path=file_path,
            line=1,
            character=0
        )
    )
    
    provider = get_o1_provider()
    try:
        await provider.initialize()
        result = await provider.suggest_refactoring(snippet, goal)
        click.echo(result)
    finally:
        await provider.close()


@analyze.command()
@click.argument("file_paths", nargs=-1, type=click.Path(exists=True))
async def architecture(file_paths: List[str]):
    """Analyze the architecture of multiple files."""
    snippets = []
    for file_path in file_paths:
        content = read_file(file_path)
        snippets.append(CodeSnippet(
            content=content,
            language=Path(file_path).suffix[1:],
            location=CodeLocation(
                path=file_path,
                line=1,
                character=0
            )
        ))
    
    provider = get_o1_provider()
    try:
        await provider.initialize()
        result = await provider.explain_architecture(snippets)
        click.echo(result)
    finally:
        await provider.close()


@cli.group()
def search():
    """Search code using Sourcegraph."""
    pass


@search.command()
@click.argument("query")
async def code(query: str):
    """Search for code using Sourcegraph."""
    indexer = get_sourcegraph_indexer()
    try:
        await indexer.initialize()
        results = await indexer.search(query)
        for result in results:
            click.echo(f"\nFile: {result.location.path}")
            click.echo(f"Line {result.location.line}, Col {result.location.character}:")
            click.echo(f"```{result.language}")
            click.echo(result.content)
            click.echo("```")
    finally:
        await indexer.close()


@search.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--line", "-l", type=int, required=True,
              help="Line number to get definition for")
@click.option("--character", "-c", type=int, required=True,
              help="Character position to get definition for")
async def definition(file_path: str, line: int, character: int):
    """Get the definition of a symbol."""
    indexer = get_sourcegraph_indexer()
    try:
        await indexer.initialize()
        result = await indexer.get_definition(file_path, line, character)
        click.echo(result)
    finally:
        await indexer.close()


@search.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--line", "-l", type=int, required=True,
              help="Line number to get references for")
@click.option("--character", "-c", type=int, required=True,
              help="Character position to get references for")
async def references(file_path: str, line: int, character: int):
    """Get references to a symbol."""
    indexer = get_sourcegraph_indexer()
    try:
        await indexer.initialize()
        results = await indexer.get_references(file_path, line, character)
        for result in results:
            click.echo(f"\nFile: {result.location.path}")
            click.echo(f"Line {result.location.line}, Col {result.location.character}:")
            click.echo(result.content)
    finally:
        await indexer.close()


def run_async(func, *args, **kwargs):
    """Run an async function."""
    return asyncio.run(func(*args, **kwargs))


def wrap_async_command(cmd):
    """Wrap an async command to run in the event loop."""
    original_callback = cmd.callback
    cmd.callback = lambda *args, **kwargs: run_async(original_callback, *args, **kwargs)


# Wrap async commands
for cmd in [
    analyze.commands["code"],
    analyze.commands["refactor"],
    analyze.commands["architecture"],
    search.commands["code"],
    search.commands["definition"],
    search.commands["references"]
]:
    wrap_async_command(cmd)
