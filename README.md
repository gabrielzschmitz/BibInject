# BibInject

<img align="right" width="256px" src="./static/icons/logov1.1.png">
  
![Version Badge](https://img.shields.io/badge/version-v1.0-pink)

**BibInject** is a Python tool for parsing `.bib` (BibTeX) files and generating
valid, styled HTML references. It supports injecting these references directly
into existing HTML files at predefined targets.

Built with simplicity in mind, BibInject helps you keep your bibliography
organized and presentation-ready without the overhead of complex pipelines. It's
perfect for blogs, project pages, or academic sites that need lightweight
citation integration without relying on JavaScript-based renderers or external
services.

Includes:
- CLI tool and Github Actions example for automation
- Optional Flask web interface

---

## 📦 Project Structure

```

bibinject/
├── src/
│   └── bibinject/
│       ├── requirements.txt # App dependencies
│       ├── app.py           # Main app entry
│       ├── cli.py           # Command-line interface
│       ├── inject.py        # HTML injection logic
│       ├── parser.py        # BibTeX parsing
│       ├── gen.py           # HTML generation
│       └── webapp.py        # Flask interface
├── static/      # Logos, CSS, icons, etc.
├── templates/   # Jinja2 HTML templates
├── setup.sh
├── bibinject.sh
├── LICENSE
└── README.md

```

---

## 🛠 Prerequisites

- [Python 3.0+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [virtualenv](https://virtualenv.pypa.io/)

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
./bibinject.sh --input="input.bib" --target-id="references" target.html
```

Options:

* `--input=<file>`: Input BibTeX file.
* `--target-id=<id>`: Inject into an element by ID.
* `--target-class=<class>`: Inject into an element by class.
* `--output=<file>`: Output to a new HTML file instead of replacing.

Example:

```sh
./bibinject.sh mypubs.bib --output="index.html"
```

---

## 🌐 Web Interface

Start a local web server:

```sh
./bibinject.sh --web
```

This allows uploading `.bib` files and downloading the updated HTML directly
from your browser.

---
    
## 🔄 Github Action
 
In `.github/workflow/inject-on-deploy.yaml` you can find a example on how to 
integrate BibInjection to your website deploy. Just make sure to run BibInject
before deploying your pages.

```yaml
name: Type Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  mypy:
    name: Injection Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup BibInject
        run: |
         ./install.sh

      - name: Run BibInject
        run: |
          DEBUG=TRUE ./run.sh \
            --input templates/refsample.bib \
            --refspec apa.html \
            --template templates/sample.html \
            --target-id my-publications \
            --order desc \
            --group year \
            output.html
            
      - name: Show resulting page
        run: |
          cat output.html

#  Deploy your page after BibInject
#  deploy:
#    environment:
#      name: github-pages
#      url: ${{ steps.deployment.outputs.page_url }}
#    runs-on: ubuntu-latest
#    needs: build
#    steps:
#      - name: Deploy to GitHub Pages
#        id: deployment
#        uses: actions/deploy-pages@v4
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE)
file for details.
