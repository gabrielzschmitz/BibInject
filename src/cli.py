import argparse
from .parser import Parser
from .gen import Generator
from .injector import Injector
from .error_handler import ErrorHandler

# Initialize error handler
error_handler = ErrorHandler()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Inject BibTeX references into an HTML template."
    )
    parser.add_argument("--input", required=True, help="Path to the BibTeX input file.")
    parser.add_argument(
        "--refspec",
        required=True,
        help="Type of reference specficiation to use (name from templates).",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="HTML template file name (from the templates/ directory).",
    )
    parser.add_argument(
        "--target-id",
        required=True,
        help="The ID of the <div> element where references should be injected.",
    )
    parser.add_argument("output", help="Output HTML file path.")
    return parser.parse_args()


@error_handler.handle
def run_cli():
    args = parse_arguments()

    # Parse BibTeX file
    parser = Parser(expand_strings=True)
    parser.parse_file(args.input)
    entries = parser.get_entries()

    if not entries:
        error_handler.error("No entries found in the input BibTeX file.")
        return

    # Generate HTML for each entry
    generated_html_blocks = []
    for entry in entries:
        html = Generator(entry, args.refspec).generate_html()
        generated_html_blocks.append(html)

    combined_html = "\n\n".join(generated_html_blocks)

    # Inject generated HTML into the target div
    injector = Injector(args.template)
    injector.save_injected_html_as(combined_html, args.target_id, args.output)
