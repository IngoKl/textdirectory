#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
import psutil
from click.testing import CliRunner

from textdirectory import helpers
from textdirectory import TextDirectory

def test_tabulate_flat_list_of_dicts():
    """Test the tabulate_flat_list_of_dicts helper."""
    dicts = [{'1':'a'}, {'2':'b'}]
    table = helpers.tabulate_flat_list_of_dicts(dicts)
    assert table == '\n|---|\n|1|\n|---|\n|a|\n|b|\n|---|'


def test_count_non_alphanum():
    """Test the count_non_alphanum helper."""
    assert helpers.count_non_alphanum('ab#cd!') == 2
    assert helpers.count_non_alphanum('***') == 3


def test_chunk_text():
    """Test the chunk_text helper."""
    chunks = helpers.chunk_text('lorem', 3)
    assert chunks == ['lor', 'em']


def test_simple_tokenizer():
    """Test the simple_tokenizer helper."""
    assert helpers.simple_tokenizer('lorem ipsum dolor sit') == ['lorem', 'ipsum', 'dolor', 'sit']


def test_estimate_spacy_max_length():
    """Test the test_estimate_spacy_max_length helper."""
    estimate = helpers.estimate_spacy_max_length()
    assert estimate <= psutil.virtual_memory().available


def test_type_token_ratio():
    """Test the type_token_ratio helper."""
    text = 'The TTR is the number of types devided by the number of tokens'
    ttr = helpers.type_token_ratio(text)
    assert ttr == 0.77


def test_get_human_from_docstring():
    """Test the get_human_from_docstring helper."""
    doc = getattr(TextDirectory, 'filter_by_min_chars').__doc__
    human_name = helpers.get_human_from_docstring(doc)['name']
    assert human_name == 'Minimum characters'


def test_get_get_available_filters():
    """Test the get_available_filters helper."""
    available_filters = helpers.get_available_filters()
    assert 'filter_by_chars_outliers' in available_filters


def test_get_get_available_filters_human():
    """Test the get_available_filters helper."""
    available_filters = helpers.get_available_filters(get_human_name=True)
    assert ('filter_by_chars_outliers', 'Character outliers') in available_filters


def test_get_available_transformations():
    """Test the get_available_transformations helper."""
    available_transformations = helpers.get_available_transformations()
    assert 'transformation_lowercase' in available_transformations


def test_get_available_transformations_human():
    """Test the get_available_transformations helper."""
    available_transformations = helpers.get_available_transformations(get_human_name=True)
    assert ('transformation_crude_spellchecker', 'transformation_crude_spellchecker') in available_transformations
