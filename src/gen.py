# Third-Party Library Imports
from pathlib import Path
import re
import os
from typing import Dict, List, Any

# Local Imports
from .error_handler import (
    ErrorHandler,
    FileNotFoundError,
    FileReadError,
    EmptyFileError,
    HTMLElementNotFoundError,
)


# Initialize Error Handling
error_handler = ErrorHandler()


class Generator:
    """
    A utility class for generating HTML strings by injecting data
    into HTML templates. Primarily used for generating bibliography
    entries dynamically.

    Attributes:
        data (dict): The dictionary containing the bibliographic entry.
        template_name (str): The HTML template file name.
        type (str): The entry type (e.g., 'article', 'book').
    """

    class _Splitter:
        """
        Internal helper class to split HTML templates into
        opening tag, middle content, and closing tag based
        on the 'bi-{type}' identifier.
        """

        def __init__(self, html: str, type_: str):
            """
            Args:
                html (str): The full HTML template content.
                type_ (str): The type of entry (e.g., 'article').
            """
            self.html = html
            self.type = type_

        def split(self) -> List[str]:
            """
            Splits the HTML into opening tag, middle content, and closing tag
            based on the <p id="bi-{type}">...</p> block.

            Returns:
                List[str]: [opening tag, middle content, closing tag]

            Raises:
                HTMLElementNotFoundError: If the block is not found.
            """
            p_pattern = re.compile(
                rf'(^[ \t]*<p\s+id="bi-{self.type}"[^>]*>\s*\n)'
                rf"(.*?)"
                rf"(^[ \t]*</p>)",
                re.DOTALL | re.MULTILINE,
            )

            match = re.search(p_pattern, self.html)
            if not match:
                raise HTMLElementNotFoundError(
                    f"Full <p id='bi-{self.type}'> block not found during split."
                )

            return list(match.groups())

    def __init__(self, entry: Dict[str, List[Any]], template_name: str, doi_icon=None):
        """
        Initializes the Generator instance.

        Args:
            entry (dict): Dictionary containing the bibliographic entry.
            template_name (str): Name of the HTML template file.
        """
        self.data = entry
        self.template_name = template_name
        self.type = str(entry["type"])
        self.doi_icon = doi_icon

    @error_handler.handle
    def _load_template(self) -> str:
        """
        Loads the HTML template content from the templates folder.

        Returns:
            str: Template content as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            FileReadError: If the file exists but is not readable.
            EmptyFileError: If the file exists but is empty.
        """
        template_filename = (
            self.template_name
            if self.template_name.endswith(".html")
            else self.template_name + ".html"
        )
        template_path = Path("refspec") / template_filename
        if not template_path.exists():
            raise FileNotFoundError(f"File not found: {template_path}")

        if not os.access(template_path, os.R_OK):
            raise FileReadError(f"File exists but is not readable: {template_path}")

        with open(template_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

        if not content:
            raise EmptyFileError(f"The template file at '{template_path}' is empty.")

        return content

    def _render(self, elements: List[str]) -> str:
        """
        Renders the HTML template by replacing placeholders with data values.

        Args:
            elements (List[str]): A list with [opening tag, middle content, closing tag].

        Returns:
            str: Rendered HTML string with placeholders replaced.

        Emits:
            Warning if a placeholder value is missing.
        """
        opening_tag = elements[0]
        middle = elements[1]
        closing_tag = elements[2]

        def replacer(match):
            key = match.group(1).strip()
            value = dict(self.data["fields"]).get(key)
            if value is None:
                error_handler.warning(f"Missing value for placeholder '{{{{{key}}}}}'")
                return ""
            return value

        middle = re.sub(r"\{\{\s*(\w+)\s*\}\}", replacer, middle)
        final_middle = self._trim(middle)
        return f"{opening_tag}{final_middle}{closing_tag}"

    def _trim(self, text: str) -> str:
        """
        Cleans up the text by removing empty parentheses, unnecessary
        punctuation, and excess spaces left after placeholder substitution.
        Preserves line breaks.

        Args:
            text (str): The text to clean.

        Returns:
            str: Cleaned text.
        """
        # Remove empty parentheses like (), ( ), (  )
        text = re.sub(r"\(\s*\)", "", text)

        # Remove spaces before commas or periods
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"\s+\.", ".", text)

        # Remove duplicate or misplaced punctuation
        text = re.sub(r",\s*,", ",", text)
        text = re.sub(r",\s*\.", ".", text)
        text = re.sub(r"\.\s*\.", ".", text)

        # Collapse multiple spaces but preserve newlines
        text = re.sub(r"[ ]{2,}", " ", text)

        # Remove leading/trailing spaces on lines but preserve newlines
        text = re.sub(r"^[ ]+|[ ]+$", "", text, flags=re.MULTILINE)

        return text

    def generate_html(self) -> str:
        """
        Generates the final HTML string by loading the template,
        splitting it into sections, rendering it with the entry data,
        and cleaning it.
    
        Returns:
            str: The fully rendered and cleaned HTML string.
        """
        template_content = self._Splitter(self._load_template(), self.type).split()
        rendered = self._render(template_content)

        # Extract DOI
        fields = dict(self.data["fields"])
        doi = fields.get("doi")

        if not doi:
            return rendered

        if self.doi_icon:  
            # HTML with an image icon
            doi_link = (
                f'\n<a href="https://doi.org/{doi}" target="_blank" '
                f'class="doi-link" aria-label="View DOI" '
                f'style="display:inline-flex; align-items:center; gap:4px;">'
                f'<img src="{self.doi_icon}" alt="DOI icon" class="doi-icon"> '
                f'DOI</a>'
            )

        else:
            # Fallback: text-only DOI link
            doi_link = (
                f'\n<a href="https://doi.org/{doi}" target="_blank" '
                f'class="doi-link" aria-label="View DOI" >DOI</a>'
            )

        rendered = re.sub(
            r"(<p[^>]*>)",
            r"\1" + doi_link,
            rendered,
            count=1,
        )
        return rendered
