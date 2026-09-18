# Third-Party Library Imports
import html
import os
import re
from pathlib import Path
from typing import Any

# Local Imports
from .error_handler import (
    EmptyFileError,
    ErrorHandler,
    FileNotFoundError,
    FileReadError,
    HTMLElementNotFoundError,
)

# Initialize Error Handling
error_handler = ErrorHandler()


def _split_author_names(author_field: Any) -> list[str]:
    """Split a BibTeX author field into a list of individual author names."""
    if not author_field:
        return []
    if isinstance(author_field, list):
        return [str(a) for a in author_field if str(a).strip()]
    return [
        a.strip()
        for a in re.split(r"\s+and\s+", str(author_field), flags=re.IGNORECASE)
        if a.strip()
    ]


def _parse_author_name(raw: str) -> tuple[str, list[str]]:
    """Return (surname, given name words) for a single author name.

    Supports both 'First von Last' and 'von Last, First' BibTeX forms.
    """
    raw = raw.strip()
    if not raw:
        return "", []
    if "," in raw:
        surname_part, given_part = raw.split(",", 1)
        surname = surname_part.strip().split()[-1] if surname_part.strip() else ""
        given = [w for w in given_part.split() if w]
    else:
        words = raw.split()
        surname = words[-1] if words else ""
        given = words[:-1]
    return surname, given


def format_authors(author_field: Any, style: str) -> str:
    """Format a BibTeX author field into APA or ABNT style.

    APA:  'Schmitz, G., Boutrik, A., & Giron, A.'
    ABNT: 'SCHMITZ, Gabriel; BOUTRIK, Alexandre; GIRON, Alexandre Augusto.'
    """
    names = _split_author_names(author_field)
    formatted: list[str] = []
    for raw in names:
        surname, given = _parse_author_name(raw)
        if not surname:
            continue
        if style == "abnt":
            given_str = " ".join(given)
            label = f"{surname.upper()}, {given_str}" if given_str else surname.upper()
        else:
            initial = f"{given[0][0].upper()}." if given else ""
            label = f"{surname}, {initial}" if initial else surname
        formatted.append(label)

    if not formatted:
        return ""
    if style == "abnt":
        return "; ".join(formatted)
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def normalize_pages(pages: Any) -> str:
    """Normalize a page range so dashes render as a single hyphen (346--347 → 346-347)."""
    text = str(pages).strip()
    text = re.sub(r"[–—]", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"\s+", "", text)
    return text


PUBLISHER_NAMES: dict[str, str] = {
    "SBC": "Sociedade Brasileira de Computação",
    "IEEE": "Institute of Electrical and Electronics Engineers",
    "ACM": "Association for Computing Machinery",
    "Springer": "Springer",
    "Elsevier": "Elsevier",
    "Wiley": "John Wiley & Sons",
}


def expand_publisher(publisher: str) -> str:
    """Expand a well-known publisher abbreviation to its full name."""
    return PUBLISHER_NAMES.get(publisher.strip(), publisher)


def city_only(address: str) -> str:
    """Reduce an address like 'Porto Alegre, RS, Brasil' to its first part."""
    return address.split(",", 1)[0].strip()


def doi_citation(doi: Any, style: str) -> str:
    """Return a printable DOI citation suffix, or an empty string when absent."""
    value = str(doi).strip() if doi else ""
    if not value:
        return ""
    if style == "abnt":
        return f"DOI: https://doi.org/{value}"
    return f"doi:{value}"


def build_bibtex(entry: dict[str, Any]) -> str:
    """
    Reconstruct a complete BibTeX entry string from parsed entry data.

    Args:
        entry (dict): Parsed entry with 'type', 'key' and 'fields'.

    Returns:
        str: A valid BibTeX entry, e.g. '@article{key, field = {value}, ...}'.
    """
    entry_type = str(entry.get("type", "misc"))
    key = str(entry.get("key", ""))
    fields = dict(entry.get("fields", {}))

    lines = [f"@{entry_type}{{{key},"]
    for field, value in fields.items():
        lines.append(f"  {field} = {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


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

        def split(self) -> list[str]:
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

    def __init__(self, entry: dict[str, list[Any]], template_name: str, doi_icon=None):
        """
        Initializes the Generator instance.

        Args:
            entry (dict): Dictionary containing the bibliographic entry.
            template_name (str): Name of the HTML template file.
        """
        self.data = entry
        self.template_name = template_name
        self.style = template_name.removesuffix(".html")
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

    def _render_fields(self) -> dict[str, Any]:
        """Return the entry fields with citation-style transformations applied.

        For the built-in 'apa'/'abnt' styles, the author list is inverted,
        page ranges are normalized, and derived placeholders for publisher
        location and DOI citation are provided.
        """
        fields = dict(self.data.get("fields", {}))

        if self.style in ("apa", "abnt"):
            fields["author"] = format_authors(fields.get("author", ""), self.style)
            if fields.get("pages"):
                fields["pages"] = normalize_pages(fields["pages"])

            fields["doi_citation"] = doi_citation(fields.get("doi"), self.style)

            publisher = fields.get("publisher")
            if publisher:
                if self.style == "abnt":
                    publisher = expand_publisher(publisher)
                address = fields.get("address")
                fields["publisher_location"] = (
                    f"{city_only(address)}: {publisher}"
                    if address
                    else publisher
                )

        return fields

    def _render(self, elements: list[str]) -> str:
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

        render_fields = self._render_fields()

        def replacer(match):
            key = match.group(1).strip()
            value = render_fields.get(key)
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

        actions = ""

        # Extract DOI
        fields = dict(self.data["fields"])
        doi = fields.get("doi")

        if doi:
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

            actions += doi_link

        # BIBTEX copy button with the full entry stored in a hidden span.
        bibtex = build_bibtex(self.data)
        bibtex_button = (
            '\n<button type="button" class="bibtex-btn" '
            'aria-label="Copy BibTeX entry">BIBTEX</button>'
            f'\n<span class="bibtex-entry" hidden>{html.escape(bibtex, quote=True)}</span>'
        )

        actions += bibtex_button

        rendered = re.sub(
            r"(<p[^>]*>)",
            r"\1" + actions,
            rendered,
            count=1,
        )
        return rendered
