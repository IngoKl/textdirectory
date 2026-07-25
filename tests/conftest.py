"""Shared fixtures and configuration for the textdirectory test suite."""

import importlib.util
from pathlib import Path

import pytest

TESTDATA = Path(__file__).resolve().parent.parent / 'textdirectory' / 'data' / 'testdata'

_HAS_SPACY_MODEL = (
    importlib.util.find_spec('spacy') is not None
    and importlib.util.find_spec('en_core_web_sm') is not None
)


def pytest_collection_modifyitems(config, items):
    """Auto-skip nlp-marked tests when spacy or the en_core_web_sm model is missing."""
    skip_nlp = pytest.mark.skip(reason='requires spacy and en_core_web_sm (pip install textdirectory[nlp])')
    for item in items:
        if 'nlp' in item.keywords and not _HAS_SPACY_MODEL:
            item.add_marker(skip_nlp)


@pytest.fixture
def testdata_dir():
    """Path to the test corpus (10 .txt files across two directory levels)."""
    return TESTDATA


@pytest.fixture
def td(testdata_dir):
    """A TextDirectory instance with the test corpus loaded (recursive, sorted)."""
    from textdirectory.textdirectory import TextDirectory

    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=True, sort=True, filetype='txt')
    return td
