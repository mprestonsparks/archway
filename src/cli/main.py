#!/usr/bin/env python3
"""Main entry point for the Archway CLI."""
import click

from cli.commands import index, query, analyze


@click.group()
def cli():
    """Archway CLI for AI-driven development."""
    pass


cli.add_command(index)
cli.add_command(query)
cli.add_command(analyze)


def main():
    """Entry point for the CLI."""
    cli()
