# Third-Party Library Imports
import bibtexparser
from typing import List
from pathlib import Path

# Local Imports
from error_handler import ErrorHandler, ParsingError, FileNotFoundError


# Initialize Error Handling
error_handler = ErrorHandler()


class Parser:
    """
    A utility class for parsing BibTeX files and extracting entries and
    comments.
    """

    def __init__(self, file_path: str):
        """
        Initializes the Parser instance and loads the BibTeX file.

        Args:
            file_path (str): Path to the BibTeX (.bib) file to be parsed.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ParsingError: If parsing the file fails or results in invalid
            blocks.
        """
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self._library = bibtexparser.parse_file(self._file_path)

        if self._library is None:
            raise ParsingError(f"An error occured while parsing {file_path}")
        elif len(self._library.failed_blocks) > 0:
            error_handler.warning(
                f"Some blocks failed to parse. Failed blocks:\
                                    {self._library.failed_blocks}"
            )
        else:
            error_handler.info("All blocks parsed successfully")

        self._entries = self._library.entries
        self._comments = self._library.comments

    def get_entries_dict(self) -> dict:
        """
        Returns all BibTeX entries as a dictionary.

        Returns:
            dict: A dictionary where keys are entry identifiers and values are
            field dictionaries. If an entry has no key, `None` is used.
        """
        entries_dict = {}

        if not self._entries:
            return {}

        for entry in self._entries:
            key = entry.key or None
            entries_dict[key] = entry.fields_dict

        return entries_dict

    def get_comments_list(self) -> List[str]:
        """
        Returns all comments from the BibTeX file.

        Returns:
            list[str]: A list of comment strings extracted from the BibTeX
            file.
        """
        if not self._comments:
            return []
        return [comment.comment for comment in self._comments]
