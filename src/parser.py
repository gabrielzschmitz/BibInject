# Third-Party Library Imports
import bibtexparser
from pathlib import Path

# Local Imports
from error_handler import (
    ErrorHandler,
    ParsingError,
    FileNotFoundError
)


# Initialize Error Handling
error_handler = ErrorHandler()


class Parser:
    """
    A utility class for parsing bibtext files.
    """

    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self._library = bibtexparser.parse_file(self._file_path)

        if self._library is None:
            raise ParsingError(f"An error occured while parsing {file_path}")
        elif len(self._library.failed_blocks) > 0:
            error_handler.warning(f"Some blocks failed to parse. Failed blocks:\
                                    {self._library.failed_blocks}")
        else:
            error_handler.info("All blocks parsed successfully")

        self._entries = self._library.entries
        self._comments = self._library.comments

    def get_entries_dict(self) -> dict:
        """returns all entries in Library as dict"""
        entries_dict = {}

        if not self._entries:
            return {}

        for entry in self._entries:
            key = entry.key or None
            entries_dict[key] = entry.fields_dict

        return entries_dict

    def get_comments_list(self) -> [str]:
        """returns all comments in Library as list"""
        if not self._comments:
            return []
        return [comment.comment for comment in self._comments]
