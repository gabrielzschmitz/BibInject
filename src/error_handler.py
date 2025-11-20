import logging
import sys
from typing import Callable, Any, Optional


class TemplateNotFoundError(Exception):
    """Raised when the specified HTML template cannot be found."""

    def __init__(self, message: Optional[str] = None):
        default: str = "HTML template file was not found."
        super().__init__(message or default)


class TemplateReadError(Exception):
    """Raised when the specified HTML template has an error at reading."""

    def __init__(self, message: Optional[str] = None):
        default: str = "Failed to read HTML template content."
        super().__init__(message or default)


class HTMLElementNotFoundError(Exception):
    """Raised when the target HTML element is not found in the HTML content."""

    def __init__(self, message: Optional[str] = None):
        default: str = "Target HTML element was not found in the HTML."
        super().__init__(message or default)


class InjectionError(Exception):
    """Raised when an error occurs during the injection of BibTeX data into the HTML."""

    def __init__(self, message: Optional[str] = None):
        default: str = "Failed to inject BibTeX content into the HTML."
        super().__init__(message or default)


class ParsingError(Exception):
    """Raised when an error occurs while attempting to parse a file."""

    def __init__(self, message: Optional[str] = None):
        default: str = "An error occurred while parsing the file."
        super().__init__(message or default)


class OrderingError(Exception):
    """Raised when an error occurs while attempting to order a entry group."""

    def __init__(self, message: Optional[str] = None):
        default: str = "An error occurred while ordering entry group."
        super().__init__(message or default)


class GroupingError(Exception):
    """Raised when an error occurs while attempting to group a entry group."""

    def __init__(self, message: Optional[str] = None):
        default: str = "An error occurred while grouping entry group."
        super().__init__(message or default)


class FileNotFoundError(Exception):
    """Raised when an error occurs when file is not found."""

    def __init__(self, message: Optional[str] = None):
        default: str = "File not found."
        super().__init__(message or default)


class FileWriteError(Exception):
    """Raised when an error occurs while attempting to write to a file."""

    def __init__(self, message: Optional[str] = None):
        default: str = "An error occurred while writing to the file."
        super().__init__(message or default)


class FileReadError(Exception):
    """Raised when an error occurs while attempting to read a file."""

    def __init__(self, message: Optional[str] = None):
        default: str = "An error occurred while reading the file."
        super().__init__(message or default)


class EmptyFileError(Exception):
    """Raised when the file passed is empty."""

    def __init__(self, message: Optional[str] = None):
        default: str = "The file is empty and cannot be processed."
        super().__init__(message or default)


class ErrorHandler:
    """
    A logging utility class that configures a logger and provides a decorator
    for automatic exception handling and logging of known errors.

    Args:
        log_file (str): Path to the log file. Defaults to '/tmp/BibInject.log'.
    """

    def __init__(self, log_file: str = "/tmp/BibInject.log"):
        self.logger: logging.Logger = logging.getLogger("BibInject")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler: logging.FileHandler = logging.FileHandler(log_file)
            console: logging.StreamHandler = logging.StreamHandler(sys.stdout)

            formatter: logging.Formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            )
            handler.setFormatter(formatter)
            console.setFormatter(formatter)

            self.logger.addHandler(handler)
            self.logger.addHandler(console)

    def handle(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to automatically log and suppress known exceptions.

        Args:
            func (Callable): The function to decorate.

        Returns:
            Callable: The wrapped function with error handling.
        """

        def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
            try:
                return func(*args, **kwargs)
            except (
                TemplateNotFoundError,
                TemplateReadError,
                InjectionError,
                HTMLElementNotFoundError,
                ParsingError,
                OrderingError,
                GroupingError,
                FileNotFoundError,
                FileWriteError,
                FileReadError,
                EmptyFileError,
            ) as e:
                self.logger.error(f"{type(e).__name__}: {e}")
                return None
            except Exception:
                self.logger.exception("Unhandled exception occurred")
                return None

        return wrapper

    def info(self, message: str) -> None:
        """Log an informational message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)

    def exception(self, message: str) -> None:
        """Log an exception message with stack trace."""
        self.logger.exception(message)
