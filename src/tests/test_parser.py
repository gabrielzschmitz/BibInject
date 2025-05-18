import textwrap
import logging
import pytest
from parser import Parser


logger = logging.getLogger(__name__)


@pytest.fixture
def sample_file(tmp_path):
    bib_content = textwrap.dedent(
        """
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
    )
    file_path = tmp_path / "test.bib"
    file_path.write_text(bib_content)
    return str(file_path)


def test_get_entries_dict(sample_file, caplog):
    caplog.set_level(logging.INFO)
    p = Parser(sample_file)
    entries = p.get_entries_dict()

    assert "Cesar2013" in entries
    assert isinstance(entries, dict)
    assert entries["Cesar2013"]["author"].value == "Jean César, Ary Costa"
    assert entries["Cesar2013"]["title"].value == "An amazing title"
    logger.info(f"entries dict: {entries}")


def test_get_comments(sample_file, caplog):
    caplog.set_level(logging.INFO)
    p = Parser(sample_file)
    comments = p.get_comments_list()

    assert isinstance(comments, list)
    assert "This is my example comment." in comments
    logger.info(f"entries list: {list}")
