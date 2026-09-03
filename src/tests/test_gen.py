import logging
import textwrap

import pytest
from src.gen import Generator, build_bibtex

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_apa_template(tmp_path):
    html_content = textwrap.dedent(
        """
    <!-- Article -->
    <p id="bi-article">
      {{author}}. ({{year}}). {{title}}. <em>{{journal}}</em>, <em>{{volume}}</em>({{number}}), {{pages}}.
    </p>
    """
    )
    path = tmp_path / "mock-apa.html"
    path.write_text(html_content, encoding="utf-8")
    logger.info(f"Template written to {path}")
    return str(path)


@pytest.fixture
def mock_entry():
    return {
        "type": "article",
        "key": "Cesar2013",
        "fields": {
            "author": "Jean César, Ary Costa",
            "title": "An amazing title",
            "year": "2013",
            "volume": "12",
            "pages": "12--23",
            "journal": "Nice Journal",
        },
    }


@pytest.fixture
def mock_entry_with_doi(mock_entry):
    entry = {**mock_entry, "fields": {**mock_entry["fields"], "doi": "10.1000/xyz"}}
    return entry


def test_splitter():
    html_content = textwrap.dedent(
        """
    <!-- Book -->
    <p id="bi-book">
      {{author}}. ({{year}}). <em>{{title}}</em>. {{publisher}}.
    </p>

    <!-- Article -->
    <p id="bi-article">
      {{author}}. ({{year}}). {{title}}. <em>{{journal}}</em>, <em>{{volume}}</em>({{number}}), {{pages}}.
    </p>
    """
    )

    s = Generator._Splitter(html_content, "article")
    out = s.split()
    logger.info(out)
    assert out == [
        '<p id="bi-article">\n',
        "  {{author}}. ({{year}}). {{title}}. <em>{{journal}}</em>, <em>{{volume}}</em>({{number}}), {{pages}}.\n",
        "</p>",
    ]


def test_render(mock_entry, mock_apa_template):
    mock_out = [
        '<p id="bi-article">\n',
        "  {{author}}. ({{year}}). {{title}}. <em>{{journal}}</em>, <em>{{volume}}</em>({{number}}), {{pages}}.\n",
        "</p>",
    ]
    g = Generator(mock_entry, mock_apa_template)
    out = g._render(mock_out)
    logger.info(repr(out))
    assert repr(out) == repr(
        '<p id="bi-article">\nJean César, Ary Costa. (2013). An amazing title. <em>Nice Journal</em>, <em>12</em>, 12--23.\n</p>'
    )


def test_generate_html(mock_entry, mock_apa_template):
    g = Generator(mock_entry, mock_apa_template)
    assert g is not None
    assert g.type == "article"
    assert g.data is not None
    logger.info(g.type)
    out = g.generate_html()
    logger.info(out)
    assert repr(out) == repr(
        '<p id="bi-article">\n'
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@article{Cesar2013,\n'
        '  author = {Jean César, Ary Costa},\n'
        '  title = {An amazing title},\n'
        '  year = {2013},\n'
        '  volume = {12},\n'
        '  pages = {12--23},\n'
        '  journal = {Nice Journal},\n'
        '}</span>\n'
        'Jean César, Ary Costa. (2013). An amazing title. <em>Nice Journal</em>, <em>12</em>, 12--23.\n'
        '</p>'
    )


def test_generate_html_with_doi(mock_entry_with_doi, mock_apa_template):
    g = Generator(mock_entry_with_doi, mock_apa_template)
    out = g.generate_html()
    logger.info(out)
    assert 'class="doi-link"' in out
    assert 'https://doi.org/10.1000/xyz' in out
    assert 'class="bibtex-btn"' in out
    assert 'class="bibtex-entry"' in out


def test_build_bibtex(mock_entry):
    expected = (
        "@article{Cesar2013,\n"
        "  author = {Jean César, Ary Costa},\n"
        "  title = {An amazing title},\n"
        "  year = {2013},\n"
        "  volume = {12},\n"
        "  pages = {12--23},\n"
        "  journal = {Nice Journal},\n"
        "}"
    )
    assert build_bibtex(mock_entry) == expected
