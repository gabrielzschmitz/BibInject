# Third-Party Library Imports
import re
import os
from pathlib import Path

# Local Imports
from .error_handler import ErrorHandler, ParsingError, FileNotFoundError, FileReadError

# Initialize Error Handling
error_handler = ErrorHandler()


class Parser:
    """
    A BibTeX parser for extracting entries, comments, preambles, and string macros from BibTeX files.
    """

    def __init__(self, expand_strings=False):
        self.expand_strings = expand_strings
        self.data = {
            "entries": [],
            "comments": [],
            "preambles": [],
            "strings": [],
        }

    @error_handler.handle
    def parse_file(self, filename):
        """
        Parses a BibTeX file from the filesystem.

        Args:
            filename (str): Path to the .bib file.

        Returns:
            dict: Parsed BibTeX data.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            FileReadError: If the file isn't readable.
            ParsingError: If the content can't be parsed properly.
        """
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        if not os.access(file_path, os.R_OK):
            raise FileReadError(f"File exists but is not readable: {filename}")

        content = file_path.read_text(encoding="utf-8")
        return self.parse_string(content)

    @error_handler.handle
    def parse_string(self, content):
        """
        Parses a BibTeX string.

        Args:
            content (str): Raw BibTeX string.

        Returns:
            dict: Parsed BibTeX data structure with entries, comments, etc.
        """
        self.data = {"entries": [], "comments": [], "preambles": [], "strings": []}
        seen_keys = {}

        # Remove line continuations and combine lines
        content = re.sub(r"\s*\n\s*", " ", content)

        pos = 0
        while True:
            at_pos = content.find("@", pos)
            if at_pos == -1:
                break

            brace_pos = content.find("{", at_pos)
            if brace_pos == -1:
                raise ParsingError(
                    f"Opening brace '{{' not found after '@' at position {at_pos}"
                )

            entry_type = content[at_pos + 1 : brace_pos].strip().lower()
            if not entry_type:
                raise ParsingError(f"Entry type missing after '@' at position {at_pos}")

            entry_content, end_pos = self._extract_brace_block(content, brace_pos)
            if entry_content is None:
                raise ParsingError(
                    f"Could not extract brace block starting at position {brace_pos}"
                )

            pos = end_pos

            if entry_type == "comment":
                self.data["comments"].append(entry_content.strip())
            elif entry_type == "preamble":
                preamble_content = entry_content.strip()
                if preamble_content.startswith('"') and preamble_content.endswith('"'):
                    preamble_content = preamble_content[1:-1]
                self.data["preambles"].append(preamble_content)
            elif entry_type == "string":
                kv = self._parse_key_value(entry_content)
                if not kv:
                    raise ParsingError(
                        f"Invalid string entry content at position {brace_pos}"
                    )
                self.data["strings"].append(kv)
            else:
                entry = self._parse_entry(entry_type, entry_content)
                key = entry.get("key")
                if not key:
                    raise ParsingError(
                        f"Missing key in entry of type '{entry_type}' at position {brace_pos}"
                    )
                if key not in seen_keys:
                    seen_keys[key] = True
                    self.data["entries"].append(entry)

        error_handler.info(
            f"Parsed string content successfully, found {len(self.data['entries'])} entries"
        )
        return self.data

    def get_entries(self):
        """Return list of parsed BibTeX entries."""
        return self.data.get("entries", [])

    def get_comments(self):
        """Return list of BibTeX comments."""
        return self.data.get("comments", [])

    def get_preambles(self):
        """Return list of BibTeX preambles."""
        return self.data.get("preambles", [])

    def get_strings(self):
        """Return list of BibTeX string macros."""
        return self.data.get("strings", [])

    def get_entry_fields(self, entry):
        """Given an entry dict, return its fields dict or None if invalid."""
        return entry.get("fields") if isinstance(entry, dict) else None

    def get_entry_field(self, entry, field_name):
        """Return value of field_name for given entry, or None if not found."""
        fields = self.get_entry_fields(entry)
        if fields:
            return fields.get(field_name)
        return None

    def get_entry_key(self, entry):
        """Return citation key of the entry, or None."""
        if isinstance(entry, dict):
            return entry.get("key")
        return None

    def get_entry_type(self, entry):
        """Return type of the entry, or None."""
        if isinstance(entry, dict):
            return entry.get("type")
        return None

    def _extract_brace_block(self, s, start):
        """
        Extract a balanced brace block from a given string.

        Args:
            s (str): The full string.
            start (int): Position of the opening brace.

        Returns:
            tuple: (content inside the braces, position after closing brace)

        Raises:
            ParsingError: If braces are unbalanced.
        """
        assert s[start] == "{"
        depth = 1
        i = start + 1
        while i < len(s) and depth > 0:
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
            i += 1
        if depth != 0:
            raise ParsingError(
                f"Unbalanced braces in entry starting at position {start}"
            )
        return s[start + 1 : i - 1], i

    def _parse_key_value(self, text):
        """
        Parse a BibTeX string macro into a key-value pair.

        Args:
            text (str): String definition content.

        Returns:
            dict: Parsed key-value pair.
        """
        parts = text.split("=", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip().strip(",").strip('"{}')
            return {key: value}
        return {}

    def _parse_entry(self, entry_type, text):
        """
        Parse a BibTeX entry into its components.

        Args:
            entry_type (str): Type of the BibTeX entry (e.g., article, book).
            text (str): Raw entry content.

        Returns:
            dict: Dictionary containing entry type, citation key, and fields.
        """
        match = re.match(r"\s*([^,]+)\s*,(.*)", text, re.DOTALL)
        if not match:
            return {"type": entry_type, "raw": text}

        citation_key = match.group(1).strip()
        fields_text = match.group(2)

        fields = {}
        while fields_text:
            field_match = re.match(
                r'\s*([\w\-]+)\s*=\s*({(?:[^{}]|{[^{}]*})*}|".*?"|[^,{}]+)\s*,?',
                fields_text,
                re.DOTALL,
            )
            if not field_match:
                break
            key = field_match.group(1).strip()
            value_raw = field_match.group(2).strip()
            value = value_raw.strip('"{} ')

            # If it's a bare word (not quoted or braced), check for macro
            if self.expand_strings and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value):
                for d in self.data["strings"]:
                    if value in d:
                        value = d[value]
                        break

            fields[key] = value
            fields_text = fields_text[field_match.end() :]

        return {"type": entry_type, "key": citation_key, "fields": fields}
