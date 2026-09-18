import logging
import textwrap

import pytest
from src.gen import (
    Generator,
    build_bibtex,
    doi_citation,
    format_authors,
    normalize_pages,
)

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


def test_format_authors_apa():
    raw = "Gabriel Schmitz and Alexandre Boutrik and Alexandre Augusto Giron"
    assert format_authors(raw, "apa") == "Schmitz, G., Boutrik, A., & Giron, A."


def test_format_authors_abnt():
    raw = "Gabriel Schmitz and Alexandre Boutrik and Alexandre Augusto Giron"
    assert (
        format_authors(raw, "abnt")
        == "SCHMITZ, Gabriel; BOUTRIK, Alexandre; GIRON, Alexandre Augusto"
    )


def test_format_authors_single():
    assert format_authors("Gabriel Schmitz", "apa") == "Schmitz, G."


def test_format_authors_two():
    assert format_authors("Laurence Ferber and Mathis Rand", "apa") == "Ferber, L., & Rand, M."


def test_format_authors_comma_form():
    assert format_authors("Giron, Alexandre Augusto", "apa") == "Giron, A."


def test_format_authors_empty():
    assert format_authors("", "apa") == ""
    assert format_authors(None, "abnt") == ""


def test_normalize_pages():
    assert normalize_pages("346--347") == "346-347"
    assert normalize_pages("12–23") == "12-23"
    assert normalize_pages("346-347") == "346-347"
    assert normalize_pages(12) == "12"


def test_doi_citation():
    assert (
        doi_citation("10.5753/sbseg_estendido.2025.10485", "apa")
        == "doi:10.5753/sbseg_estendido.2025.10485"
    )
    assert (
        doi_citation("10.5753/sbseg_estendido.2025.10485", "abnt")
        == "DOI: https://doi.org/10.5753/sbseg_estendido.2025.10485"
    )
    assert doi_citation("", "apa") == ""
    assert doi_citation(None, "abnt") == ""


@pytest.fixture
def sbseg_entry():
    return {
        "type": "inproceedings",
        "key": "sbseg_estendido",
        "fields": {
            "author": "Gabriel dos Santos Schmitz and Alexandre Boutrik and Alexandre Augusto Giron",
            "title": "Towards Faster and Scalable Post-Quantum Hyperledger Fabric",
            "booktitle": "Anais Estendidos do XXV Simpósio Brasileiro de Cibersegurança",
            "location": "Foz do Iguaçu/PR",
            "year": "2025",
            "issn": "0000-0000",
            "pages": "346--347",
            "publisher": "SBC",
            "address": "Porto Alegre, RS, Brasil",
            "doi": "10.5753/sbseg_estendido.2025.10485",
        },
    }


def test_generate_html_apa(sbseg_entry):
    g = Generator(sbseg_entry, "apa")
    out = g.generate_html()
    assert "Schmitz, G., Boutrik, A., & Giron, A. (2025)." in out
    assert "Towards Faster and Scalable Post-Quantum Hyperledger Fabric." in out
    assert "In <em>Anais Estendidos do XXV Simpósio Brasileiro de Cibersegurança</em>, (pp. 346-347)." in out
    assert "Porto Alegre: SBC." in out
    assert "doi:10.5753/sbseg_estendido.2025.10485" in out


def test_generate_html_abnt(sbseg_entry):
    g = Generator(sbseg_entry, "abnt")
    out = g.generate_html()
    assert (
        "SCHMITZ, Gabriel dos Santos; BOUTRIK, Alexandre; GIRON, Alexandre Augusto."
        in out
    )
    assert "In: <em>Anais Estendidos do XXV Simpósio Brasileiro de Cibersegurança</em>. p. 346-347." in out
    assert "Porto Alegre: Sociedade Brasileira de Computação, 2025." in out
    assert "DOI: https://doi.org/10.5753/sbseg_estendido.2025.10485" in out
