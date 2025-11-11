import logging
import pytest
import textwrap
from src.gen import Generator
from src.parser import Parser


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
        '<p id="bi-article">\nJean César, Ary Costa. (2013). An amazing title. <em>Nice Journal</em>, <em>12</em>, 12--23.\n</p>'
    )


def test_generate_ordered_grouped_html(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    entries = [
        {
            "type": "article",
            "key": "Doe2024b",
            "fields": {
                "author": "John Doe",
                "title": "Deep Learning Advances",
                "year": "2024",
                "month": "March",
                "journal": "AI Journal",
                "volume": "5",
                "pages": "10--20",
            },
        },
        {
            "type": "article",
            "key": "Doe2024a",
            "fields": {
                "author": "John Doe",
                "title": "Neural Methods Overview",
                "year": "2024",
                "month": "January",
                "journal": "Neural Computation",
                "volume": "4",
                "pages": "1--9",
            },
        },
        {
            "type": "article",
            "key": "Smith2023",
            "fields": {
                "author": "Alice Smith",
                "title": "Quantum AI Foundations",
                "year": "2023",
                "journal": "Quantum Journal",
                "volume": "2",
                "pages": "30--45",
            },
        },
    ]

    html_template = textwrap.dedent(
        """
    <!-- Article -->
    <p id="bi-article">
      {{author}}. ({{year}}). {{title}}. <em>{{journal}}</em>, <em>{{volume}}</em>, {{pages}}.
    </p>
    """
    )
    template_path = tmp_path / "apa.html"
    template_path.write_text(html_template, encoding="utf-8")

    rendered_entries = []
    for entry in entries:
        g = Generator(entry, str(template_path))
        rendered_entries.append(g.generate_html())

    parser = Parser()
    ordered = parser.order_entries(entries, reverse=True)
    grouped = parser.group_entries(ordered, by="year/month", reverse=True)
    html = parser.group_entries_to_html(grouped)

    logger.info(f"Grouped ordered HTML:\n{html}")

    assert "<h2>2024</h2>" in html
    assert "<h3>March</h3>" in html
    assert "Deep Learning Advances" in html
    assert "Neural Methods Overview" in html
    assert "<h2>2023</h2>" in html
    assert "Quantum AI Foundations" in html

    years = [line for line in html.splitlines() if line.startswith("<h2>")]
    assert years[0] == "<h2>2024</h2>"
    assert years[-1] == "<h2>2023</h2>"

    assert any("Grouped ordered HTML" in msg for msg in caplog.messages)
