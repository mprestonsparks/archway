"""Main entry point for Archway CLI."""
import sys

from src.cli.commands import cli


def main():
    """Run the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
