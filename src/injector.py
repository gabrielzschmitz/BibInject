# Third-Party Library Imports
import re
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Injector:
    """
    A utility class for injecting HTML snippets into a specific <div> by ID within an HTML template file.
    """

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)

        if not self.template_path.exists():
            logger.error("Template file '%s' does not exist.",
                         self.template_path)
            raise FileNotFoundError(f"Template not found: {template_path}")

        try:
            self.html = self.template_path.read_text(encoding='utf-8')
            logger.info("Loaded template from '%s'", template_path)
        except OSError as e:
            logger.error("Error reading file '%s': %s",
                         template_path, e)
            raise


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
        # Regex to find the opening line of the <div> with the given ID and
        # capture its indentation
        try:
            open_div_pattern = re.compile(
                rf'^(?P<indent>[ \t]*)<div\s+id="{target_id}"[^>]*>\s*\n',
                re.MULTILINE
            )
            open_div_match = open_div_pattern.search(self.html)
            if not open_div_match:
                raise ValueError(
                    f"Could not find opening <div id=\"{target_id}\">."
                )
            base_indent = open_div_match.group('indent')
            logger.debug("Base indentation detected: '%s'", base_indent)
        except re.error as e:
            logger.error("Regex error: %s", e)
            raise

        # Determine the indentation unit used in the file
        indent_unit = "  "  # default 2 spaces
        for line in self.html.splitlines():
            stripped = line.lstrip()
            if stripped and len(line) > len(stripped):
                indent_unit = line[:len(line) - len(stripped)]
                logger.debug("Detected indent unit: '%s'", indent_unit)
                break

        # Properly indent the lines of HTML to inject
        inject_lines = html_to_inject.strip('\n').splitlines()
        indented_html = "\n".join(
            f"{base_indent}{indent_unit}{line}"
            for line in inject_lines
        )

        # Pattern to replace the entire <div> content
        try:
            logger.debug("Performing content injection for <div id='%s'>",
                         target_id)
            full_div_pattern = re.compile(
                rf'(^[ \t]*<div\s+id="{target_id}"[^>]*>\s*\n)'
                rf'(.*?)'
                rf'(^[ \t]*</div>)',
                re.DOTALL | re.MULTILINE
            )

            def replacement(match):
                opening_line = match.group(1)
                closing_line = match.group(3)
                return f"{opening_line}{indented_html}\n{closing_line}"

            result = full_div_pattern.sub(replacement, self.html)
            logger.info("HTML successfully injected into <div id=\"%s\">",
                        target_id)
        except re.error as e:
            logger.error("Regex substitution error: %s", e)
            raise

        return result


    def save_injected_html_as(self, html_to_inject: str, target_id: str, output_path: str) -> None:
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
        try:
            Path(output_path).write_text(result, encoding='utf-8')
            logger.info("Injected HTML saved to '%s'", output_path)
        except OSError as e:
            logger.error("Error writing file '%s': %s", output_path, e)
            raise


    def replace_template_with_injected_html(self, html_to_inject: str, target_id: str) -> None:
        """
        Overwrites the original template file with the injected HTML content.

        Args:
            html_to_inject (str): HTML string to be injected inside the target <div>.
            target_id (str): The ID of the <div> where the content should be inserted.

        Raises:
            OSError: If writing to the template file fails.
        """
        result = self.inject_html(html_to_inject, target_id)
        try:
            self.template_path.write_text(result, encoding='utf-8')
            logger.info("Replaced original file '%s'", self.template_path)
        except OSError as e:
            logger.error("Error writing to '%s': %s", self.template_path, e)
            raise
