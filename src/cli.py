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
    parser.add_argument("--input", required=True, help="Path to the BibTeX input file (.bib).")
    parser.add_argument(
        "--refspec",
        required=True,
        help="Path or name of the HTML reference specification template.",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Target HTML template file into which references are injected.",
    )
    parser.add_argument(
        "--target-id",
        required=True,
        help="The ID of the <div> or element where references should be injected.",
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="desc",
        help="Order of entries by year/month. Use 'asc' for oldest first or 'desc' for most recent first (default).",
    )
    parser.add_argument(
        "--group",
        help="Optional field name to group entries by year/month.",
    )
    parser.add_argument(
        "output",
        help="Output HTML file path where the final injected HTML will be written.",
    )
    return parser.parse_args()


@error_handler.handle
def run_cli():
    args = parse_arguments()

    # Step 1: Parse BibTeX
    parser = Parser(expand_strings=True)
    data = parser.parse_file(args.input)
    entries = data.get("entries", [])
    if not entries:
        error_handler.error("No valid BibTeX entries found.")
        return

    # Step 2: Order entries (reverse=True for desc)
    reverse_order = args.order == "desc"
    entries = parser.order_entries(entries, reverse=reverse_order)

    # Step 3: Group entries if requested
    grouped_entries = None
    if args.group:
        grouped_entries = parser.group_entries(entries, by=args.group)
    else:
        grouped_entries = {"All": entries}

    # Step 4: Generate HTML for each group
    generated_blocks = []
    for group_name, group_items in grouped_entries.items():
        group_html = []
        for entry in group_items:
            html = Generator(entry, args.refspec).generate_html()
            group_html.append(html)
    
        # Optionally add a header per group
        if args.group:
            group_header = f"<h2>{group_name}</h2>"
            generated_blocks.append(group_header + "\n" + "\n\n".join(group_html))
        else:
            generated_blocks.append("\n\n".join(group_html))
    
    combined_html = "\n\n".join(generated_blocks)
    
    # Step 5: Inject HTML into target template
    injector = Injector(args.template)
    injector.save_injected_html_as(combined_html, args.target_id, args.output)
