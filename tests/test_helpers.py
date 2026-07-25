"""Tests for the helpers module."""

import pytest

from textdirectory import TextDirectory, helpers


def test_tabulate_flat_list_of_dicts():
    """Test the tabulate_flat_list_of_dicts helper."""
    dicts = [{'1': 'a'}, {'2': 'b'}]
    table = helpers.tabulate_flat_list_of_dicts(dicts)
    assert table == '\n|---|\n|1|\n|---|\n|a|\n|b|\n|---|'


def test_tabulate_empty_list_returns_empty_string():
    """An empty list tabulates to '' (regression: returned False)."""
    assert helpers.tabulate_flat_list_of_dicts([]) == ''


def test_tabulate_truncates_long_values():
    """Cell values are truncated to max_length."""
    table = helpers.tabulate_flat_list_of_dicts([{'col': 'abcdefghij'}], max_length=3)
    assert 'abc' in table
    assert 'abcd' not in table


def test_count_non_alphanum():
    """Test the count_non_alphanum helper."""
    assert helpers.count_non_alphanum('ab#cd!') == 2
    assert helpers.count_non_alphanum('***') == 3

    # Digits are alphanumeric (regression: they were counted as non-alphanumeric)
    assert helpers.count_non_alphanum('1945') == 0
    assert helpers.count_non_alphanum('a1!') == 1


def test_chunk_text():
    """Test the chunk_text helper."""
    chunks = helpers.chunk_text('lorem', 3)
    assert chunks == ['lor', 'em']


def test_simple_tokenizer():
    """Test the simple_tokenizer helper."""
    assert helpers.simple_tokenizer('lorem ipsum dolor sit') == ['lorem', 'ipsum', 'dolor', 'sit']


@pytest.mark.nlp
def test_estimate_spacy_max_length():
    """Test the estimate_spacy_max_length helper."""
    import psutil

    estimate = helpers.estimate_spacy_max_length()
    assert estimate <= psutil.virtual_memory().available


def test_estimate_spacy_max_length_override():
    """An override is returned directly (and needs no psutil)."""
    assert helpers.estimate_spacy_max_length(override=1234) == 1234


def test_type_token_ratio():
    """Test the type_token_ratio helper."""
    text = 'The TTR is the number of types devided by the number of tokens'
    ttr = helpers.type_token_ratio(text)
    assert ttr == 0.77


def test_type_token_ratio_empty_text():
    """Empty text yields a TTR of 0.0 (regression: ZeroDivisionError)."""
    assert helpers.type_token_ratio('') == 0.0


def test_coerce_args_by_signature():
    """String args are coerced to the types the target signature suggests."""
    coerced = helpers.coerce_args_by_signature(TextDirectory.filter_by_max_chars, ['50'])
    assert coerced == [50]

    coerced = helpers.coerce_args_by_signature(TextDirectory.filter_by_type_token_ratio, ['0.4', '0.8'])
    assert coerced == [0.4, 0.8]

    coerced = helpers.coerce_args_by_signature(TextDirectory.filter_by_random_sampling, ['3', 'True'])
    assert coerced == ['3', True]

    # String parameters stay strings, even when they look numeric
    coerced = helpers.coerce_args_by_signature(TextDirectory.filter_by_contains, ['2024'])
    assert coerced == ['2024']


def test_coerce_args_by_signature_for_transformations():
    """Boolean transformation arguments coming from the CLI are coerced, not left truthy."""
    from textdirectory.transformations import transformation_remove_weird_tokens

    coerced = helpers.coerce_args_by_signature(transformation_remove_weird_tokens, ['en_core_web_sm', 'False'])
    assert coerced == ['en_core_web_sm', False]

    coerced = helpers.coerce_args_by_signature(transformation_remove_weird_tokens, ['en_core_web_sm', 'True'])
    assert coerced == ['en_core_web_sm', True]


def test_get_human_from_docstring_without_docstring():
    """A missing docstring yields no human name instead of raising."""
    assert helpers.get_human_from_docstring(None) == {}
    assert helpers.get_human_from_docstring('') == {}


def test_get_available_filters_is_strict():
    """Only real filter_by_* methods are discovered (regression: substring matching)."""
    available_filters = helpers.get_available_filters()
    assert all(name.startswith('filter_by_') for name in available_filters)
    assert 'filter' not in available_filters
    assert 'load_files' not in available_filters


def test_get_available_transformations_is_strict():
    """Only real transformation_* functions are discovered."""
    available_transformations = helpers.get_available_transformations()
    assert all(name.startswith('transformation_') for name in available_transformations)
    assert 'CrudeSpellChecker' not in available_transformations


def test_get_human_from_docstring():
    """Test the get_human_from_docstring helper."""
    doc = TextDirectory.filter_by_min_chars.__doc__
    human_name = helpers.get_human_from_docstring(doc)['name']
    assert human_name == 'Minimum characters'


def test_get_available_filters():
    """Test the get_available_filters helper."""
    available_filters = helpers.get_available_filters()
    assert 'filter_by_chars_outliers' in available_filters


def test_get_available_filters_human():
    """Test the get_available_filters helper with human names."""
    available_filters = helpers.get_available_filters(get_human_name=True)
    assert ('filter_by_chars_outliers', 'Character outliers') in available_filters


def test_get_available_transformations():
    """Test the get_available_transformations helper."""
    available_transformations = helpers.get_available_transformations()
    assert 'transformation_lowercase' in available_transformations


def test_get_available_transformations_human():
    """Test the get_available_transformations helper with human names."""
    available_transformations = helpers.get_available_transformations(get_human_name=True)
    assert ('transformation_crude_spellchecker', 'transformation_crude_spellchecker') in available_transformations
