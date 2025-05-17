import logging
import pytest
from parser import Parser


logger = logging.getLogger(__name__)


@pytest.fixture
def template_file(tmp_path):
    bib_content = """
@comment{
    This is my example comment.
}

@ARTICLE{Cesar2013,
  author = {Jean César, Ary Costa},
  title = {An amazing title},
  year = {2013},
  volume = {12},
  pages = {12--23},
  journal = {Nice Journal}
}
"""
    file_path = tmp_path / "test.bib"
    file_path.write_text(bib_content)
    return str(file_path)


def test_get_entries_dict(template_file, caplog):
    caplog.set_level(logging.INFO)
    p = Parser(template_file)
    entries = p.get_entries_dict()

    assert "Cesar2013" in entries
    assert isinstance(entries, dict)
    assert entries["Cesar2013"]["author"].value == "Jean César, Ary Costa"
    assert entries["Cesar2013"]["title"].value == "An amazing title"
    logger.info(f"entries dict: {entries}")


def test_get_comments(template_file, caplog):
    caplog.set_level(logging.INFO)
    p = Parser(template_file)
    comments = p.get_comments()

    assert isinstance(comments, list)
    assert "This is my example comment." in comments
    logger.info(f"entries list: {list}")
