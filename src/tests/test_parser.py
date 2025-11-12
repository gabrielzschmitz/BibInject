import textwrap
import logging
import pytest
from src.parser import Parser

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_bib_content():
    return textwrap.dedent(
        """
        @comment{
            This is my example comment.
        }

        @preamble{
            "This is a preamble."
        }

        @string{NJ = "Nice Journal"}

        @ARTICLE{Cesar2013,
          author = {Jean César, Ary Costa},
          title = {An amazing title},
          year = {2013},
          volume = {12},
          pages = {12--23},
          journal = {NJ}
        }

        @ARTICLE{Cesar2013,
          author = {Duplicate entry that should be ignored},
          title = {Duplicate title},
          year = {2013}
        }
        """
    )


def test_parse_string_and_dedup(sample_bib_content, caplog):
    caplog.set_level(logging.INFO)
    parser = Parser(expand_strings=True)
    result = parser.parse_string(sample_bib_content)

    logger.info(f"Parsed result keys: {list(result.keys())}")
    logger.info(f"Comments: {result['comments']}")
    logger.info(f"Preambles: {result['preambles']}")
    logger.info(f"Strings: {result['strings']}")
    logger.info(f"Entries keys: {[e.get('key') for e in result['entries']]}")

    assert "entries" in result
    assert "comments" in result
    assert "preambles" in result
    assert "strings" in result

    assert "This is my example comment." in result["comments"]
    assert "This is a preamble." in result["preambles"]

    keys = [e.get("key") for e in result["entries"]]
    assert keys.count("Cesar2013") == 1  # Deduplication

    entry = next(e for e in result["entries"] if e["key"] == "Cesar2013")
    assert len(entry) > 0
    logger.info(f"Entry for Cesar2013: {entry}")
    assert entry["fields"]["author"] == "Jean César, Ary Costa"
    assert entry["fields"]["title"] == "An amazing title"

    # NJ expansion test
    assert entry["fields"]["journal"] == "Nice Journal"

    # Check that logs contain expected keys info
    assert any("Parsed result keys" in message for message in caplog.messages)


def test_parse_file_and_getters(tmp_path, sample_bib_content, caplog):
    caplog.set_level(logging.INFO)
    file_path = tmp_path / "test.bib"
    file_path.write_text(sample_bib_content)

    parser = Parser()
    parser.parse_file(str(file_path))

    logger.info(f"Entries loaded: {len(parser.get_entries())}")
    logger.info(f"Comments loaded: {parser.get_comments()}")
    logger.info(f"Preambles loaded: {parser.get_preambles()}")
    logger.info(f"Strings loaded: {parser.get_strings()}")

    entries = parser.get_entries()
    assert isinstance(entries, list)
    assert all(isinstance(e, dict) for e in entries)

    comments = parser.get_comments()
    assert isinstance(comments, list)
    assert "This is my example comment." in comments

    preambles = parser.get_preambles()
    assert isinstance(preambles, list)
    assert "This is a preamble." in preambles

    strings = parser.get_strings()
    assert isinstance(strings, list)
    assert any("NJ" in s for s in strings)

    # Confirm logs have relevant info
    assert any("Entries loaded" in message for message in caplog.messages)
    assert any("Comments loaded" in message for message in caplog.messages)


def test_entry_helpers(sample_bib_content, caplog):
    caplog.set_level(logging.INFO)
    parser = Parser()
    parser.parse_string(sample_bib_content)

    entry = parser.get_entries()[0]

    fields = parser.get_entry_fields(entry)
    logger.info(f"Entry fields: {fields}")
    assert isinstance(fields, dict)
    assert fields.get("author") is not None

    author = parser.get_entry_field(entry, "author")
    logger.info(f"Author field: {author}")
    assert author == fields["author"]
    assert parser.get_entry_field(entry, "nonexistent") is None

    key = parser.get_entry_key(entry)
    logger.info(f"Entry key: {key}")
    assert key == entry.get("key")

    typ = parser.get_entry_type(entry)
    logger.info(f"Entry type: {typ}")
    assert typ == entry.get("type")

    # Check logs mention fields and author
    assert any("Entry fields" in message for message in caplog.messages)
    assert any("Author field" in message for message in caplog.messages)


def test_get_entry_helpers_with_invalid_input(caplog):
    caplog.set_level(logging.INFO)
    parser = Parser()

    assert parser.get_entry_fields(None) is None
    assert parser.get_entry_field(None, "author") is None
    assert parser.get_entry_key(None) is None
    assert parser.get_entry_type(None) is None

    assert parser.get_entry_fields("not a dict") is None
    assert parser.get_entry_field("not a dict", "author") is None
    assert parser.get_entry_key("not a dict") is None
    assert parser.get_entry_type("not a dict") is None

    logger.info("Invalid input tests passed")
    assert any("Invalid input tests passed" in message for message in caplog.messages)

def test_group_and_order_entries(caplog):
    caplog.set_level(logging.INFO)
    parser = Parser()

    # Simulated parsed entries
    entries = [
        {
            "type": "article",
            "key": "Doe2023a",
            "fields": {
                "author": "John Doe",
                "title": "Earlier Paper",
                "year": "2023",
                "month": "January",
            },
        },
        {
            "type": "article",
            "key": "Doe2024b",
            "fields": {
                "author": "John Doe",
                "title": "Most Recent Paper",
                "year": "2024",
                "month": "March",
            },
        },
        {
            "type": "article",
            "key": "Doe2024a",
            "fields": {
                "author": "John Doe",
                "title": "Second Paper",
                "year": "2024",
                "month": "January",
            },
        },
        {
            "type": "article",
            "key": "Smith2022",
            "fields": {
                "author": "Alice Smith",
                "title": "Oldest Paper",
                "year": "2022",
            },
        },
    ]

    # ---- ORDER TEST ----
    ordered = parser.order_entries(entries, reverse=True)
    logger.info(f"Ordered entries: {[e['fields']['title'] for e in ordered]}")

    assert ordered[0]["fields"]["title"] == "Most Recent Paper"
    assert ordered[-1]["fields"]["title"] == "Oldest Paper"

    # ---- GROUP TEST (year/month) ----
    grouped = parser.group_entries(entries, by="year/month", reverse=True)
    logger.info(f"Grouped keys: {list(grouped.keys())}")
    logger.info(f"2024 months: {list(grouped['2024'].keys())}")

    assert list(grouped.keys()) == ["2024", "2023", "2022"]
    assert "March" in grouped["2024"]
    assert "January" in grouped["2024"]
    assert grouped["2024"]["March"][0]["fields"]["title"] == "Most Recent Paper"

    # ---- HTML RENDER TEST (optional) ----
    html = parser.group_entries_to_html(grouped)
    logger.info(f"Generated HTML:\n{html}")

    assert "<h2>2024</h2>" in html
    assert "<h3>March</h3>" in html
    assert "Most Recent Paper" in html

    # ---- Logging Assertions ----
    assert any("Ordered entries" in m for m in caplog.messages)
    assert any("Grouped keys" in m for m in caplog.messages)
