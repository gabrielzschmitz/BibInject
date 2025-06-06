"""
Main Application Entry Point.

This module initializes and runs the BibInject application.
"""

# Local Imports
from src import __version__, __author__
from src.cli import run_cli


def main():
    """
    Entry point for application logic.
    """
    print(f"BibInject v{__version__} by {__author__}\n")
    run_cli()


if __name__ == "__main__":
    """
    Initializes and runs the app.
    """
    main()
