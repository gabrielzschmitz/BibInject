from flask import Flask, render_template, request, send_file
from io import BytesIO

from .data import UIData
from .injector import Injector
from .error_handler import ErrorHandler

app = Flask(__name__, template_folder="../templates", static_folder="../static")
error_handler = ErrorHandler()

last_output_html = ""


@app.route("/", methods=["GET"])
def index():
    """Landing page with upload form."""
    data = UIData()  # load all UI values
    return render_template("web.html", data=data)


@app.route("/inject", methods=["POST"])
def inject_web():
    """Receive form data, run the inject pipeline, and return output HTML."""

    global last_output_html, last_input_filename

    # Read HTML input (file or textarea)
    html_text = ""
    filename = None
    if "htmlfile" in request.files and request.files["htmlfile"].filename:
        file = request.files["htmlfile"]
        filename = file.filename
        html_text = file.read().decode("utf-8")
    else:
        html_text = request.form.get("htmltext", "")

    last_input_filename = filename 

    # Read BibTeX input (file or textarea)
    bib_text = ""
    if "bibfile" in request.files and request.files["bibfile"].filename:
        bib_text = request.files["bibfile"].read().decode("utf-8")
    else:
        bib_text = request.form.get("bibtext", "")

    # Other fields
    style = request.form.get("style")
    order = request.form.get("order")
    group = request.form.get("group")
    target_id = request.form.get("target_id")

    # Run the processing pipeline
    output_html = Injector.run_injection_pipeline(
        html_text=html_text,
        bib_text=bib_text,
        style=style,
        order=order,
        group=group,
        target_id=target_id,
    )

    last_output_html = output_html

    data = UIData()
    return render_template("web.html", data=data, output=output_html)


@app.route("/download", methods=["POST"])
def download_output():
    global last_input_filename

    html_content = request.form.get("output")
    if not html_content:
        return "No output to download.", 400

    # If no file uploaded, use default name
    input_name = last_input_filename or "output.html"

    # Split extension safely
    if "." in input_name:
        base, ext = input_name.rsplit(".", 1)
        output_name = f"{base}-injected.{ext}"
    else:
        output_name = input_name + "-injected.html"

    buffer = BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer, as_attachment=True, download_name=output_name, mimetype="text/html"
    )


@app.route("/preview")
def preview():
    global last_output_html
    if not last_output_html:
        return "<p>No output generated yet</p>"
    return last_output_html


def run_web(host="127.0.0.1", port=6969):
    """Entry point used by run.sh --web"""
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_web()
