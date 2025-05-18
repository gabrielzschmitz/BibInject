import logging
import sys
from typing import Callable, Any


class TemplateNotFoundError(Exception):
    """Raised when the specified HTML template cannot be found."""

    def __init__(self, message=None):
        default = "HTML template file was not found."
        super().__init__(message or default)


class TemplateReadError(Exception):
    """Raised when the specified HTML template have a error at reading."""

    def __init__(self, message=None):
        default = "Failed to read HTML template content."
        super().__init__(message or default)


class DivNotFoundError(Exception):
    """Raised when the target <div> element is not found in the HTML content."""

    def __init__(self, message=None):
        default = "Target <div> element was not found in the HTML."
        super().__init__(message or default)


class InjectionError(Exception):
    """Raised when an error occurs during the injection of BibTeX data into the HTML."""

    def __init__(self, message=None):
        default = "Failed to inject BibTeX content into the HTML."
        super().__init__(message or default)


class ParsingError(Exception):
    """Raised when an error occurs while attempting to parse a file."""

    def __init__(self, message=None):
        default = "An error occurred while parsing the file."
        super().__init__(message or default)


class FileNotFoundError(Exception):
    """Raised when an error occurs when file is not found."""

    def __init__(self, message=None):
        default = "File not found."
        super().__init__(message or default)


class FileWriteError(Exception):
    """Raised when an error occurs while attempting to write to a file."""

    def __init__(self, message=None):
        default = "An error occurred while writing to the file."
        super().__init__(message or default)


class FileReadError(Exception):
    """Raised when an error occurs while attempting to read a file."""

    def __init__(self, message=None):
        default = "An error occurred while reading the file."
        super().__init__(message or default)


class ErrorHandler:
    """
    A logging utility class that configures a logger and provides a decorator
    for automatic exception handling and logging of known errors.

    Args:
        log_file (str): Path to the log file. Defaults to '/tmp/BibInject.log'.
    """

    def __init__(self, log_file: str = "/tmp/BibInject.log"):
        self.logger = logging.getLogger("BibInject")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            console = logging.StreamHandler(sys.stdout)

            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            console.setFormatter(formatter)

            self.logger.addHandler(handler)
            self.logger.addHandler(console)

    def handle(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to automatically log and suppress known exceptions.

        Catches TemplateNotFoundError, TemplateReadError, DivNotFoundError,
        InjectionError, ParsingError, FileWriteError and FileReadError
        logs the error message, and suppresses the exception.
        Logs any other unhandled exceptions with the stack trace.

        Args:
            func (Callable): The function to decorate.

        Returns:
            Callable: The wrapped function with error handling.
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (
                TemplateNotFoundError,
                TemplateReadError,
                DivNotFoundError,
                InjectionError,
                ParsingError,
                FileNotFoundError,
                FileWriteError,
                FileReadError,
            ) as e:
                self.logger.error(f"{type(e).__name__}: {e}")
            except Exception:
                self.logger.exception("Unhandled exception occurred")

        return wrapper

    # Logging methods
    def info(self, message: str):
        """
        Log an informational message.
        """
        self.logger.info(message)

    def warning(self, message: str):
        """
        Log a warning message.
        """
        self.logger.warning(message)

    def error(self, message: str):
        """
        Log an error message.
        """
        self.logger.error(message)

    def exception(self, message: str):
        """
        Log an exception message with stack trace.
        """
        self.logger.exception(message)
