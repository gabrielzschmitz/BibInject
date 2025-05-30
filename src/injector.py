# Third-Party Library Imports
import re
from pathlib import Path

# Local Imports
from .error_handler import (
    ErrorHandler,
    TemplateNotFoundError,
    TemplateReadError,
    DivNotFoundError,
    InjectionError,
    FileWriteError,
)


# Initialize Error Handling
error_handler = ErrorHandler()


class Injector:
    """
    A utility class for injecting HTML snippets into a specific <div> by ID within an HTML template file.
    """

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)

        if not self.template_path.exists():
            raise TemplateNotFoundError(f"Template not found: {template_path}")

        self.html = self._read_template()

        error_handler.info(f"Loaded template from '{template_path}'")

    def _read_template(self) -> str:
        content = self.template_path.read_text(encoding="utf-8")
        if not content:
            raise TemplateReadError(
                f"Template is empty or unreadable: {self.template_path}"
            )
        return content

    @error_handler.handle
    def inject_html(self, html_to_inject: str, target_id: str) -> str:
        """
        Injects HTML content into a <div> with the specified ID in an HTML file.

        Args:
            template_path (str): Path to the HTML template file.
            html_to_inject (str): HTML string to be injected inside the target <div>.
            target_id (str): The ID of the <div> where the content should be inserted.

        Returns:
            str: Modified HTML content with the injected HTML inside the specified <div>.

        Raises:
            ValueError: If the target <div id="{target_id}"> is not found.
            OSError: If there is an issue reading the file.
        """
        open_div_pattern = re.compile(
            rf'^(?P<indent>[ \t]*)<div\s+id="{target_id}"[^>]*>\s*\n', re.MULTILINE
        )
        open_div_match = open_div_pattern.search(self.html)
        if not open_div_match:
            raise DivNotFoundError(f"Could not find <div id='{target_id}'>")

        base_indent = open_div_match.group("indent")
        indent_unit = self._detect_indent_unit()

        inject_lines = html_to_inject.strip("\n").splitlines()
        indented_html = "\n".join(
            f"{base_indent}{indent_unit}{line}" for line in inject_lines
        )

        full_div_pattern = re.compile(
            rf'(^[ \t]*<div\s+id="{target_id}"[^>]*>\s*\n)'
            rf"(.*?)"
            rf"(^[ \t]*</div>)",
            re.DOTALL | re.MULTILINE,
        )

        if not full_div_pattern.search(self.html):
            raise InjectionError(
                f"Full <div id='{target_id}'> block not found for injection."
            )

        result = full_div_pattern.sub(
            lambda match: f"{match.group(1)}{indented_html}\n{match.group(3)}",
            self.html,
        )

        error_handler.info(f"HTML successfully injected into <div id='{target_id}'>")
        return result

    def _detect_indent_unit(self) -> str:
        for line in self.html.splitlines():
            stripped = line.lstrip()
            if stripped and len(line) > len(stripped):
                return line[: len(line) - len(stripped)]
        return "  "  # fallback to 2 spaces

    @error_handler.handle
    def save_injected_html_as(
        self, html_to_inject: str, target_id: str, output_path: str
    ) -> None:
        """
        Saves the HTML with the injected content into a new file.

        Args:
            html_to_inject (str): HTML string to be injected inside the target <div>.
            target_id (str): The ID of the <div> where the content should be inserted.
            output_path (str): Path to write the modified HTML file.

        Raises:
            OSError: If writing to the output file fails.
        """
        result = self.inject_html(html_to_inject, target_id)
        path = Path(output_path)

        if path.exists() and not path.is_file():
            raise FileWriteError(
                f"Output path '{output_path}' exists but is not a file."
            )

        written = path.write_text(result, encoding="utf-8")
        if written is None:
            raise FileWriteError(f"Failed to write to '{output_path}'")

        error_handler.info(f"Injected HTML saved to '{output_path}'")

    @error_handler.handle
    def replace_template_with_injected_html(
        self, html_to_inject: str, target_id: str
    ) -> None:
        """
        Overwrites the original template file with the injected HTML content.

        Args:
            html_to_inject (str): HTML string to be injected inside the target <div>.
            target_id (str): The ID of the <div> where the content should be inserted.

        Raises:
            OSError: If writing to the template file fails.
        """
        result = self.inject_html(html_to_inject, target_id)

        written = self.template_path.write_text(result, encoding="utf-8")
        if written is None:
            raise FileWriteError(f"Failed to write to template '{self.template_path}'")

        error_handler.info(f"Replaced original file '{self.template_path}'")
