"""
Main Application Entry Point.

This module initializes and runs the BibInject application.
"""

# Third-Party Library Imports


# Local Imports
from BibInject import __version__, __author__


def main():
    """
    Entry point for application logic.
    """
    print(f"BibInject v{__version__} by {__author__}\n")


if __name__ == "__main__":
    """
    Initializes and runs the app.
    """
    main()
