"""Tests for the CrudeSpellChecker."""

import gzip
import pickle

import pytest

from textdirectory.crudespellchecker import CrudeSpellChecker, generate_crudespellchecker_lm


@pytest.fixture(scope='module')
def spellchecker():
    """A shared spellchecker instance (the language model is ~4 MB to load)."""
    return CrudeSpellChecker()


def test_correction(spellchecker):
    """A misspelled word is corrected."""
    assert spellchecker.correction('spellling') == 'spelling'


def test_correction_preserves_capitalization(spellchecker):
    """The initial capitalization survives the correction."""
    assert spellchecker.correction('Spellling') == 'Spelling'


def test_correction_populates_cache(spellchecker):
    """Corrections are cached under the misspelled word (regression: wrong cache key)."""
    spellchecker.correction('spelling')
    spellchecker.correction('spellling')

    assert spellchecker.cache.get('spellling') == 'spelling'


def test_correct_string_handles_punctuation_only_tokens(spellchecker):
    """Tokens without word characters are passed through (regression: IndexError)."""
    corrected = spellchecker.correct_string('Hello --- world !!')

    assert '---' in corrected
    assert '!!' in corrected


def test_correct_string_return_corrections(spellchecker):
    """The return_corrections flag returns the applied corrections."""
    corrected, corrections = spellchecker.correct_string('one spellling mistake', return_corrections=True)

    assert 'spelling' in corrected
    assert ('spellling', 'spelling') in corrections


def test_init_is_silent(capsys):
    """Instantiating the spellchecker prints nothing (regression: stray debug print)."""
    CrudeSpellChecker()
    out, err = capsys.readouterr()
    assert out == ''


def test_generate_crudespellchecker_lm(tmp_path, monkeypatch):
    """A language model can be generated from a corpus directory."""
    corpus = tmp_path / 'corpus'
    corpus.mkdir()
    (corpus / 'a.txt').write_text('hello hello world', encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    generate_crudespellchecker_lm(str(corpus), 'test_lm')

    with gzip.open(tmp_path / 'test_lm.gz.lm', 'rb') as lm:
        frequencies = pickle.load(lm)

    assert frequencies['hello'] == 2
    assert frequencies['world'] == 1
