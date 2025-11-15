from flask import Flask, render_template, request, send_file
from io import BytesIO

from .data import UIData
from .injector import Injector
from .error_handler import ErrorHandler

app = Flask(__name__, template_folder="../templates", static_folder="../static")
error_handler = ErrorHandler()


@app.route("/", methods=["GET"])
def index():
    """Landing page with upload form."""
    data = UIData()  # load all UI values
    return render_template("web.html", data=data)


@app.route("/inject", methods=["POST"])
def inject_web():
    """Receive form data, run the inject pipeline, and return output HTML."""

    # Read HTML input (file or textarea)
    html_text = ""
    if "htmlfile" in request.files and request.files["htmlfile"].filename:
        html_text = request.files["htmlfile"].read().decode("utf-8")
    else:
        html_text = request.form.get("htmltext", "")

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

    data = UIData()
    return render_template("web.html", data=data, output=output_html)


@app.route("/download", methods=["POST"])
def download_output():
    html_content = request.form.get("output")

    if not html_content:
        return "No output to download.", 400

    buffer = BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="output.html",
        mimetype="text/html"
    )

def run_web(host="127.0.0.1", port=5000):
    """Entry point used by run.sh --web"""
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_web()
