# Third-Party Library Imports
import bibtexparser
import logging

# Local Imports

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Parser:
    """
    A utility class for parsing bibtext files.
    """

    def __init__(self, file: str):
        self._library = bibtexparser.parse_file(file)
        if len(self._library.failed_blocks) > 0:
            logger.warning("Some blocks failed to parse. Failed blocks: %s.",
                           self._library.failed_blocks)
        else:
            logger.info("All blocks parsed successfully")

        self._entries = self._library.entries

    def get_entries_dict(self) -> dict:
        """returns all entries in a Library as a dict"""
        entries_dict = {}

        if not self._entries:
            return entries_dict

        for entry in self._entries:
            key = entry.key or None
            entries_dict[key] = entry.fields_dict

        return entries_dict

    def get_comments(self) -> [str]:
        """returns all comments in a Library as a list"""
        return [comment.comment for comment in self._library.comments]
