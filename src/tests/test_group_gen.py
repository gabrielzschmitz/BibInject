import logging

import pytest
from src.group_gen import BIBTEX_SCRIPT, GroupHTMLGenerator

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

    ordered = group_gen.order_entries(entries=entries, reverse=True, group=None)
    grouped = group_gen.group_entries(entries=ordered, by="year/month", reverse=True)
    html = group_gen.render_groups(grouped, reverse=True)
    logger.error(f"niiger3: {html} ")

    booklet2_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@booklet{CitekeyBooklet2,\n'
        '  title = {Hiking Routes Near Stockholm},\n'
        '  author = {Erik Lindstrom and Maria Swetla},\n'
        '  howpublished = {Distributed at the Stockholm Hiking Association},\n'
        '  month = {mar},\n'
        '  year = {2015},\n'
        '}</span>'
    )
    booklet_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@booklet{CitekeyBooklet,\n'
        '  title = {Canoe tours in Sweden},\n'
        '  author = {Maria Swetla and Leonard Susskind},\n'
        '  howpublished = {Distributed at the Stockholm Tourist Office},\n'
        '  month = {jul},\n'
        '  year = {2015},\n'
        '}</span>'
    )
    book_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@book{CitekeyBook,\n'
        '  author = {Leonard Susskind and George Hrabovsky},\n'
        '  title = {Classical mechanics: the theoretical minimum},\n'
        '  publisher = {Penguin Random House},\n'
        '  address = {New York, NY},\n'
        '  year = {2014},\n'
        '}</span>'
    )

    expected_html = (
        "<h2>2015</h2>\n"
        "<h3>March</h3>\n\n"
        '<p id="bi-booklet">\n' + booklet2_button +
        "\nLINDSTROM, Erik; SWETLA, Maria. <em>Hiking Routes Near Stockholm</em>. "
        "Distributed at the Stockholm Hiking Association, mar 2015.\n"
        "</p>\n\n"
        "<h3>July</h3>\n\n"
        '<p id="bi-booklet">\n' + booklet_button +
        "\nSWETLA, Maria; SUSSKIND, Leonard. <em>Canoe tours in Sweden</em>. "
        "Distributed at the Stockholm Tourist Office, jul 2015.\n"
        "</p>\n\n"
        "<h2>2014</h2>\n"
        "<h3>Unknown</h3>\n\n"
        '<p id="bi-book">\n' + book_button +
        "\nSUSSKIND, Leonard; HRABOVSKY, George. <em>Classical mechanics: "
        "the theoretical minimum</em>. New York: Penguin Random House, 2014.\n"
        "</p>" + BIBTEX_SCRIPT
    )

    assert html == expected_html


def test_render_by_author_asc(group_gen, entries):

    ordered = group_gen.order_entries(entries=entries, group="author", reverse=False)
    grouped = group_gen.group_entries(entries=ordered, by="author", reverse=False)
    html = group_gen.render_groups(grouped, reverse=False)
    logger.error(f"niiger: {html} ")

    booklet2_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@booklet{CitekeyBooklet2,\n'
        '  title = {Hiking Routes Near Stockholm},\n'
        '  author = {Erik Lindstrom and Maria Swetla},\n'
        '  howpublished = {Distributed at the Stockholm Hiking Association},\n'
        '  month = {mar},\n'
        '  year = {2015},\n'
        '}</span>'
    )
    booklet_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@booklet{CitekeyBooklet,\n'
        '  title = {Canoe tours in Sweden},\n'
        '  author = {Maria Swetla and Leonard Susskind},\n'
        '  howpublished = {Distributed at the Stockholm Tourist Office},\n'
        '  month = {jul},\n'
        '  year = {2015},\n'
        '}</span>'
    )
    book_button = (
        '<button type="button" class="bibtex-btn" aria-label="Copy BibTeX entry">BIBTEX</button>\n'
        '<span class="bibtex-entry" hidden>@book{CitekeyBook,\n'
        '  author = {Leonard Susskind and George Hrabovsky},\n'
        '  title = {Classical mechanics: the theoretical minimum},\n'
        '  publisher = {Penguin Random House},\n'
        '  address = {New York, NY},\n'
        '  year = {2014},\n'
        '}</span>'
    )

    def booklet2():
        return (
            '<p id="bi-booklet">\n' + booklet2_button +
            "\nLINDSTROM, Erik; SWETLA, Maria. <em>Hiking Routes Near Stockholm</em>. "
            "Distributed at the Stockholm Hiking Association, mar 2015.\n"
            "</p>"
        )

    def booklet():
        return (
            '<p id="bi-booklet">\n' + booklet_button +
            "\nSWETLA, Maria; SUSSKIND, Leonard. <em>Canoe tours in Sweden</em>. "
            "Distributed at the Stockholm Tourist Office, jul 2015.\n"
            "</p>"
        )

    def book():
        return (
            '<p id="bi-book">\n' + book_button +
            "\nSUSSKIND, Leonard; HRABOVSKY, George. <em>Classical mechanics: "
            "the theoretical minimum</em>. New York: Penguin Random House, 2014.\n"
            "</p>"
        )

    expected_html = "\n\n".join(
        [
            f"<h2>Erik Lindstrom</h2>\n{booklet2()}",
            f"<h2>George Hrabovsky</h2>\n{book()}",
            f"<h2>Leonard Susskind</h2>\n{book()}\n\n{booklet()}",
            f"<h2>Maria Swetla</h2>\n{booklet2()}\n\n{booklet()}",
        ]
    ) + BIBTEX_SCRIPT

    assert html == expected_html
