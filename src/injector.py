# Third-Party Library Imports
import re
from typing import Optional
from pathlib import Path

# Local Imports
from .parser import Parser
from .group_gen import GroupHTMLGenerator
from .error_handler import (
    ErrorHandler,
    TemplateNotFoundError,
    TemplateReadError,
    HTMLElementNotFoundError,
    InjectionError,
    FileWriteError,
)


# Initialize Error Handling
error_handler = ErrorHandler()


class Injector:
    """
    A utility class for injecting HTML snippets into a specific <div> by ID within an HTML template file.
    """

    def __init__(self, template: str, *, is_path: bool = True):
        """
        template:
            - if is_path=True → treat as filesystem path
            - if is_path=False → treat as raw HTML text (already loaded)
        """
        self.template_path: Optional[Path] = None
        self.is_path = is_path

        if is_path:
            self.template_path = Path(template)

            if not self.template_path.exists():
                raise TemplateNotFoundError(f"Template not found: {template}")

            self.html = self._read_template()
            error_handler.info(f"Loaded template from '{template}'")

        else:
            if not template.strip():
                raise TemplateReadError("Provided template HTML is empty.")

            self.html = template
            error_handler.info("Loaded template from string input.")

    def _read_template(self) -> str:
        assert self.template_path is not None
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
        # Accepts id="x" or id='x'
        id_attr = rf'id=["\']{target_id}["\']'

        # Match the opening div, regardless of quotes
        open_div_pattern = re.compile(
            rf"^(?P<indent>[ \t]*)<div\s+[^>]*{id_attr}[^>]*>",
            re.MULTILINE,
        )
        open_div_match = open_div_pattern.search(self.html)

        if not open_div_match:
            raise HTMLElementNotFoundError(f"Could not find <div id='{target_id}'>")

        base_indent = open_div_match.group("indent")
        indent_unit = self._detect_indent_unit()

        inject_lines = html_to_inject.strip("\n").splitlines()
        indented_html = "\n".join(
            f"{base_indent}{indent_unit}{line}" for line in inject_lines
        )

        # Full block matcher: handles:
        #   <div ...> ... </div>
        #   <div ...></div>
        #   <div ...>   </div>
        full_div_pattern = re.compile(
            rf"(?P<open><div\s+[^>]*{id_attr}[^>]*>)"
            rf"(?P<inner>.*?)"
            rf"(?P<close></div>)",
            re.DOTALL,
        )

        match = full_div_pattern.search(self.html)
        if not match:
            raise InjectionError(
                f"Full <div id='{target_id}'> block not found for injection."
            )

        open_tag = match.group("open")
        close_tag = match.group("close")

        # If one-liner (<div id="x"></div>), add newline/indentation
        if match.group("inner").strip() == "":
            new_inner = f"\n{indented_html}\n{base_indent}"
        else:
            # Multi-line div
            new_inner = f"\n{indented_html}\n{base_indent}"

        result = (
            self.html[: match.start()]
            + f"{open_tag}{new_inner}{close_tag}"
            + self.html[match.end() :]
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

        assert self.template_path is not None
        written = self.template_path.write_text(result, encoding="utf-8")
        if written is None:
            raise FileWriteError(f"Failed to write to template '{self.template_path}'")

        error_handler.info(f"Replaced original file '{self.template_path}'")

    def run_injection_pipeline(html_text, bib_text, style, order, group, target_id):
        """Runs the BibInject pipeline using form or CLI values and returns final HTML."""

        # ---- 1. Parse BibTeX ----
        parser = Parser(expand_strings=True)
        data = parser.parse_string(bib_text)
        entries = data.get("entries", [])
        if not entries:
            return "Error: No valid BibTeX entries found."

        # Step 2: Order entries (reverse=True for desc)
        html_gen = GroupHTMLGenerator(style)
        reverse_order = order == "desc"
        entries = html_gen.order_entries(entries, reverse=reverse_order, group=group)

        # Step 3: Group entries
        grouped = (
            html_gen.group_entries(entries, by=group) if group else {"All": entries}
        )

        # Step 4: Generate HTML for each group
        combined_html = html_gen.render_groups(grouped, reverse=reverse_order)

        # ---- 5. Inject final HTML ----
        injector = Injector(html_text, is_path=False)
        final_html = injector.inject_html(combined_html, target_id)

        return final_html
