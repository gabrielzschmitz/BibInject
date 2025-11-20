# BibInject

<img align="right" width="256px" src="./static/icons/logov1.1.png">
  
![Version Badge](https://img.shields.io/github/v/release/gabrielzschmitz/BibInject?color=pink)

**BibInject** is a Python tool for parsing `.bib` (BibTeX) files and generating
valid, styled HTML references. It supports injecting these references directly
into existing HTML files at predefined targets.

Built with simplicity in mind, BibInject helps you keep your bibliography
organized and presentation-ready without the overhead of complex pipelines.
It's perfect for blogs, project pages, or academic sites that need lightweight
citation integration without relying on JavaScript-based renderers or external
services.

Includes:
- CLI tool and Github Actions example for automation
- Optional Flask web interface

---

## 🛠️ Prerequisites

- [Python 3.0+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [virtualenv](https://virtualenv.pypa.io/)
- [Flask](https://flask.palletsprojects.com/en/stable/)

---

## 🚀 Installation

### 1. Clone the repository

```sh
git clone https://github.com/gabrielzschmitz/BibInject.git
cd BibInject
````

### 2. Run the setup to install all dependencies

```sh
./setup.sh
```

---

## ⚙️ CLI Usage

Convert a `.bib` file and inject the result into an HTML element:

```sh
./bibinject.sh              \
    --input input.bib       \
    --refspec apa           \
    --html target.html      \
    --target-id references  \
    --order desc            \
    --group year            \
    output.html
```

Options:

* `--input=<file>`:
  Path to the BibTeX (`.bib`) file containing the reference entries to be
processed.

* `--refspec=<name>`:
  Reference formatting style (e.g., `apa`, `abnt`). Determines how the
citations will be rendered.

* `--html=<file>`:
  Path to the HTML file into which the generated reference list will be
injected.

* `--target-id=<id>`:
  The `id` attribute of the `<div>` in the HTML file where the references
should be inserted.

* `--order=<asc|desc>`:
  Sorting order for the references (ascending or descending). Usually based on
year.

* `--group=<field>`:
  Group the output by a BibTeX field (e.g., `year`, `author`). Groups are
rendered as section headers.

* `<output>` (positional argument):
  Output HTML file to write, containing the injected reference list.

---

## 🌐 Web Interface

Start a local web server:

```sh
./bibinject.sh --web
```

This launches a browser-friendly interface where you can upload `.bib` files,
preview the injected output, and download the updated HTML at:

`http://127.0.0.1:6969`

If you prefer not to run the app locally or install anything, you can use the
hosted version of **BibInject** at:

**[https://bibinject.vercel.app](https://bibinject.vercel.app)**

---

## 🔄 GitHub Action Integration

You can automate BibInject as part of your deployment workflow. An example is
provided in `.github/workflow/inject-on-deploy.yaml`, showing how to run
BibInject before publishing your website. This ensures your citation list is
always regenerated and up-to-date on every deploy.

```yaml
name: Injection Action

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  bibinject:
    name: Injection Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install BibInject
        run: |
          ./install.sh

      - name: Run BibInject
        run: |
          DEBUG=TRUE ./bibinject.sh \
            --input samples/refsample.bib \
            --refspec apa \
            --html samples/sample.html \
            --target-id my-publications \
            --order desc \
            --group year \
            output.html

      - name: Show resulting page
        run: cat output.html

# Deploy your page only after BibInject has completed.
# deploy:
#   environment:
#     name: github-pages
#     url: ${{ steps.deployment.outputs.page_url }}
#   runs-on: ubuntu-latest
#   needs: bibinject
#   steps:
#     - name: Deploy to GitHub Pages
#       id: deployment
#       uses: actions/deploy-pages@v4
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE)
file for details.
