import textwrap
import pytest

import logging
from src.group_gen import GroupHTMLGenerator

logger = logging.getLogger(__name__)


@pytest.fixture
def group_gen():
    return GroupHTMLGenerator("abnt")


@pytest.fixture
def entries():
    return [
        {
            "type": "book",
            "key": "CitekeyBook",
            "fields": {
                "author": "Leonard Susskind and George Hrabovsky",
                "title": "Classical mechanics: the theoretical minimum",
                "publisher": "Penguin Random House",
                "address": "New York, NY",
                "year": "2014",
            },
        },
        {
            "type": "booklet",
            "key": "CitekeyBooklet",
            "fields": {
                "title": "Canoe tours in Sweden",
                "author": "Maria Swetla and Leonard Susskind",
                "howpublished": "Distributed at the Stockholm Tourist Office",
                "month": "jul",
                "year": "2015",
            },
        },
        {
            "type": "booklet",
            "key": "CitekeyBooklet2",
            "fields": {
                "title": "Hiking Routes Near Stockholm",
                "author": "Erik Lindstrom and Maria Swetla",
                "howpublished": "Distributed at the Stockholm Hiking Association",
                "month": "mar",
                "year": "2015",
            },
        },
    ]


def test_render_year_month_desc(group_gen, entries):
    """
    group_gen: fixture that returns your BibParser instance
    """

    ordered = group_gen.order_entries(entries=entries, reverse=True, group=None)
    grouped = group_gen.group_entries(entries=ordered, by="year/month", reverse=True)
    html = group_gen.render_groups(grouped, reverse=True)

    expected_html = textwrap.dedent(
        """
        <div id="my-publications">
          <h2>2015</h2>
          <h3>March</h3>

          <p id="bi-booklet">
          Erik Lindstrom and Maria Swetla. <em>Hiking Routes Near Stockholm</em>. Distributed at the Stockholm Hiking Association, mar 2015.
          </p>

          <h3>July</h3>

          <p id="bi-booklet">
          Maria Swetla and Leonard Susskind. <em>Canoe tours in Sweden</em>. Distributed at the Stockholm Tourist Office, jul 2015.
          </p>

          <h2>2014</h2>
          <h3>Unknown</h3>

          <p id="bi-book">
          Leonard Susskind and George Hrabovsky. <em>Classical mechanics: the theoretical minimum</em>. Penguin Random House, 2014.
          </p>
        </div>
    """
    ).strip()

    assert "2015" in html
    assert "2014" in html

    assert html.index("2015") < html.index("2014")

    assert html.index("<h3>March</h3>") < html.index("<h3>July</h3>")

    assert "Hiking Routes Near Stockholm" in html
    assert "Canoe tours in Sweden" in html
    assert "Classical mechanics: the theoretical minimum" in html


def test_render_by_author_asc(group_gen, entries):

    ordered = group_gen.order_entries(entries=entries, group="author", reverse=False)
    grouped = group_gen.group_entries(entries=ordered, by="author", reverse=False)
    html = group_gen.render_groups(grouped, reverse=False)

    expected_html = textwrap.dedent(
        """
        <div id="my-publications">
          <h2>Erik Lindstrom</h2>
          <p id="bi-booklet">
          Erik Lindstrom and Maria Swetla. <em>Hiking Routes Near Stockholm</em>. Distributed at the Stockholm Hiking Association, mar 2015.
          </p>

          <h2>George Hrabovsky</h2>
          <p id="bi-book">
          Leonard Susskind and George Hrabovsky. <em>Classical mechanics: the theoretical minimum</em>. Penguin Random House, 2014.
          </p>

          <h2>Leonard Susskind</h2>
          <p id="bi-book">
          Leonard Susskind and George Hrabovsky. <em>Classical mechanics: the theoretical minimum</em>. Penguin Random House, 2014.
          </p>

          <p id="bi-booklet">
          Maria Swetla and Leonard Susskind. <em>Canoe tours in Sweden</em>. Distributed at the Stockholm Tourist Office, jul 2015.
          </p>

          <h2>Maria Swetla</h2>
          <p id="bi-booklet">
          Erik Lindstrom and Maria Swetla. <em>Hiking Routes Near Stockholm</em>. Distributed at the Stockholm Hiking Association, mar 2015.
          </p>

          <p id="bi-booklet">
          Maria Swetla and Leonard Susskind. <em>Canoe tours in Sweden</em>. Distributed at the Stockholm Tourist Office, jul 2015.
          </p>
        </div>
    """
    ).strip()

    order = [
        "Erik Lindstrom",
        "George Hrabovsky",
        "Leonard Susskind",
        "Maria Swetla",
    ]

    prev_index = -1
    for author in order:
        idx = html.index(f"<h2>{author}</h2>")
        assert idx > prev_index
        prev_index = idx

    assert "Hiking Routes Near Stockholm" in html
    assert "Canoe tours in Sweden" in html
    assert "Classical mechanics: the theoretical minimum" in html
