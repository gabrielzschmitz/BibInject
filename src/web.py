from flask import Flask, render_template

from .data import UIData
from .error_handler import ErrorHandler

app = Flask(__name__, template_folder="../templates", static_folder="../static")
error_handler = ErrorHandler()


@app.route("/", methods=["GET"])
def index():
    """Landing page with upload form."""
    data = UIData()  # load all UI values
    return render_template("web.html", data=data)


def run_web(host="127.0.0.1", port=5000):
    """Entry point used by run.sh --web"""
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_web()
