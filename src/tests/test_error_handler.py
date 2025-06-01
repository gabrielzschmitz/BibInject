import logging
from src.error_handler import (
    TemplateNotFoundError,
    TemplateReadError,
    HTMLElementNotFoundError,
    InjectionError,
    ParsingError,
    FileNotFoundError,
    FileWriteError,
    FileReadError,
    ErrorHandler,
    EmptyFileError,
)

logger = logging.getLogger(__name__)


def test_custom_error_messages():
    # Test exception message when custom message provided
    assert str(TemplateNotFoundError("Missing file")) == "Missing file"
    assert str(TemplateReadError("Read failed")) == "Read failed"
    assert str(InjectionError("Bad injection")) == "Bad injection"
    assert str(ParsingError("Parsing failed")) == "Parsing failed"
    assert str(FileNotFoundError("File missing")) == "File missing"
    assert str(FileWriteError("Write failed")) == "Write failed"
    assert str(FileReadError("Read failed")) == "Read failed"
    assert str(EmptyFileError("Empty file")) == "Empty file"
    assert (
        str(HTMLElementNotFoundError("HTML element missing")) == "HTML element missing"
    )


def test_default_error_messages():
    # Test exception message when no custom message provided (default)
    assert str(TemplateNotFoundError()) == "HTML template file was not found."
    assert str(TemplateReadError()) == "Failed to read HTML template content."
    assert str(InjectionError()) == "Failed to inject BibTeX content into the HTML."
    assert str(ParsingError()) == "An error occurred while parsing the file."
    assert str(FileNotFoundError()) == "File not found."
    assert str(FileWriteError()) == "An error occurred while writing to the file."
    assert str(FileReadError()) == "An error occurred while reading the file."
    assert str(EmptyFileError()) == "The file is empty and cannot be processed."
    assert (
        str(HTMLElementNotFoundError())
        == "Target HTML element was not found in the HTML."
    )


def test_error_handler_logging_info(caplog):
    handler = ErrorHandler()
    caplog.set_level(logging.INFO)

    handler.info("This is an info log.")
    assert "This is an info log." in caplog.text
    assert any(record.levelname == "INFO" for record in caplog.records)


def test_error_handler_logging_warning(caplog):
    handler = ErrorHandler()
    caplog.set_level(logging.WARNING)

    handler.warning("This is a warning.")
    assert "This is a warning." in caplog.text
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_error_handler_logging_error(caplog):
    handler = ErrorHandler()
    caplog.set_level(logging.ERROR)

    handler.error("This is an error!")
    assert "This is an error!" in caplog.text
    assert any(record.levelname == "ERROR" for record in caplog.records)
