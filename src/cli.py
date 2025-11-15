import argparse
from .error_handler import ErrorHandler
from .injector import Injector
from .web import run_web

# Initialize error handler
error_handler = ErrorHandler()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Inject BibTeX references into an HTML template."
    )

    # --- WEB MODE (optional, triggers early exit) ---
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start the BibInject web interface.",
    )

    # --- CLI MODE ARGS (no longer required=True here) ---
    parser.add_argument("--input", help="Path to the BibTeX input file (.bib).")
    parser.add_argument(
        "--refspec",
        help="Path or name of the HTML reference specification template.",
    )
    parser.add_argument(
        "--template",
        help="Target HTML template file into which references are injected.",
    )
    parser.add_argument(
        "--target-id",
        help="The ID of the <div> or element where references should be injected.",
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="desc",
        help="Order of entries by year/month.",
    )
    parser.add_argument(
        "--group",
        help="Optional field name to group entries by year/month.",
    )

    # Positional output (optional in web mode)
    parser.add_argument(
        "output",
        nargs="?",
        help="Output HTML file path where the final injected HTML will be written.",
    )

    return parser.parse_args()


@error_handler.handle
def run_cli():
    args = parse_arguments()

    # If --web is set, ignore all other arguments and start the web server
    if args.web:
        print("Starting BibInject web interface on http://127.0.0.1:6969 ...")
        return run_web()

    # ---- Load template HTML ----
    with open(args.template, "r", encoding="utf-8") as f:
        html_text = f.read()

    # ---- Load BibTeX file ----
    with open(args.input, "r", encoding="utf-8") as f:
        bib_text = f.read()

    # ---- Run the unified pipeline ----
    output_html = Injector.run_injection_pipeline(
        html_text=html_text,
        bib_text=bib_text,
        style=args.refspec,
        order=args.order,
        group=args.group,
        target_id=args.target_id,
    )

    # If pipeline returned an error, show it
    if output_html.startswith("Error:"):
        error_handler.error(output_html)
        return

    # ---- Save output ----
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"Injected HTML saved to {args.output}")
