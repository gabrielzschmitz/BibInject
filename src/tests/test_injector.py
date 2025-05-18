import textwrap
import logging
import pytest
from injector import Injector

logger = logging.getLogger(__name__)


@pytest.fixture
def template_file(tmp_path):
    html_content = textwrap.dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <title>Sample Template</title>
          </head>

          <body>
            <h1>Checkout my papers!</h1>

            <div id="my-publications">
            </div>

            <footer>
              <p>
              The publications section was created automatically. <br>
              Isn't it cool?
              </p>
            </footer>
          </body>
        </html>
    """
    )
    path = tmp_path / "sample-template.html"
    path.write_text(html_content, encoding="utf-8")
    logger.info(f"Template written to {path}")
    return path


def test_inject_html(template_file, caplog):
    html_to_inject = textwrap.dedent(
        """
        <div class="injected-section">
          <h2>Injected Section</h2>
          <p>This content was dynamically added!</p>
          <ul>
            <li>First item</li>
            <li>Second item</li>
          </ul>
        </div>
    """
    )

    expected_injected = """<div id="my-publications">
      <div class="injected-section">
        <h2>Injected Section</h2>
        <p>This content was dynamically added!</p>
        <ul>
          <li>First item</li>
          <li>Second item</li>
        </ul>
      </div>
    </div>"""

    caplog.set_level(logging.INFO)
    injector = Injector(template_file)
    result = injector.inject_html(html_to_inject, "my-publications")

    logger.info("Injection result:\n%s", result)

    if expected_injected not in result:
        logger.error("Expected injected block was not found in the result.")
        logger.debug("Expected:\n%s", expected_injected)
        logger.debug("Actual:\n%s", result)
        pytest.fail("Injected HTML block was not found in the output.")

    count = result.count('<div class="injected-section">')
    if count != 1:
        logger.error("Expected 1 injected section, but found %d", count)
        logger.debug("Result HTML:\n%s", result)
        pytest.fail(f"Expected 1 injected section, but found {count}")


def test_save_injected_html_as_creates_new_file(template_file, tmp_path, caplog):
    injector = Injector(template_file)
    html_to_inject = "<p>Saved HTML</p>"
    output_path = tmp_path / "output.html"

    caplog.set_level(logging.INFO)
    injector.save_injected_html_as(html_to_inject, "my-publications", output_path)

    assert output_path.exists(), "Output file was not created"
    contents = output_path.read_text(encoding="utf-8")
    assert "<p>Saved HTML</p>" in contents, "Injected content not found in saved file"

    assert any(
        f"Injected HTML saved to '{output_path}'" in message
        for message in caplog.messages
    ), "Expected log message not found for save operation"


def test_replace_template_with_injected_html_overwrites_original(template_file, caplog):
    injector = Injector(template_file)
    html_to_inject = "<span>Overwritten HTML</span>"

    original_content = template_file.read_text(encoding="utf-8")
    assert "<span>Overwritten HTML</span>" not in original_content

    caplog.set_level(logging.INFO)
    injector.replace_template_with_injected_html(html_to_inject, "my-publications")

    new_content = template_file.read_text(encoding="utf-8")
    assert (
        "<span>Overwritten HTML</span>" in new_content
    ), "Original template was not updated"

    assert any(
        f"Replaced original file '{template_file}'" in message
        for message in caplog.messages
    ), "Expected log message not found for replace operation"
