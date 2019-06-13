#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory
from textdirectory.transformations import transformation_remove_non_ascii, transformation_remove_non_alphanumerical, \
    transformation_to_leetspeak, transformation_crude_spellchecker, transformation_remove_stopwords, \
    transformation_remove_htmltags
from textdirectory import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert 'TextDirectory' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert 'Usage' in help_result.output


def test_simpple_aggregations():
    """Test the simplest form of aggregation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    assert len(td.aggregate_to_memory()) == 4083


def test_filter_by_chars_outliers():
    """Test the outlier filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_chars_outliers(1)
    assert len(td.aggregation) == 7


def test_filter_by_similar_documents():
    """Test the similarity filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_similar_documents(reference_file='data/testdata/level_2/Text_E.txt', threshold=0.7)
    assert len(td.aggregation) == 2


def test_filter_by_max_filesize():
    """Test the filesize (max) filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_max_filesize(max_kb=1)
    assert len(td.aggregation) == 7


def test_filter_by_min_filesize():
    """Test the filesize (min) filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_min_filesize(min_kb=2)
    assert len(td.aggregation) == 1


def test_transformation_remove_nl():
    """Test the remove_nl transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_remove_nl'])
    assert '\n' not in td.aggregate_to_memory()


def test_transformation_remove_htmltags():
    """Test the remove htmltags transformation."""
    test_string = '<html><body>This <span id="1">is</span> a <em>test</em></body></html>'
    assert transformation_remove_htmltags(test_string) == 'This is a test'


def test_transformation_uppercase():
    """Test the uppercase transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_uppercase'])
    assert td.aggregate_to_memory().isupper()


def test_transformation_remove_non_ascii_hard():
    """Test the remove non-ascii transformation."""
    test_string = 'This is a @ test string ~ containing non-ascii characters such as 😁.'
    assert transformation_remove_non_ascii(test_string) == 'This is a @ test string ~ containing non-ascii characters such as .'


def test_transformation_remove_non_ascii_easy():
    """Test the remove non-alphanumerical transformation."""
    test_string = 'non-alphanumerical @ / - * .'
    assert transformation_remove_non_alphanumerical(test_string).strip() == 'nonalphanumerical'


def test_transformation_to_leetspeak():
    """Test the leetspeak transformation."""
    test_string = 'leetspeak'
    assert transformation_to_leetspeak(test_string) == '133tsp34k'


def test_transformation_crude_spellchecker():
    """Test the crude spellchecker transformation."""
    test_string = 'There are two spellling mistaces in here.'
    assert transformation_crude_spellchecker(test_string) == 'There are two spelling mistakes in here.'


def test_transformation_remove_stopwords():
    """Test the remove stopwords transformation."""
    test_string = 'There is a house on the hill.'
    assert transformation_remove_stopwords(test_string) == 'There is house hill.'


def test_transformation_test_arguments():
    """Test whether we can pass arguments to transformations."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_remove_stopwords', 'internal', 'en', 'en_core_web_sm',
                             'dolor,dolore,dolores'])
    text = td.aggregate_to_memory()
    assert 'dolor' not in text


#def test_transformation_postag():
#    """Test the postag transformation."""
#    td = TextDirectory(directory='data/testdata/')
#    td.load_files(True, 'txt')
#    td.stage_transformation(['transformation_postag'])
#    assert 'NN' in td.aggregate_to_memory()


def test_tabulation(capsys):
    """Test the tabulation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.print_aggregation()
    out, err = capsys.readouterr()
    assert 'path' in out


def test_transform_to_memory():
    """Test the in memory transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.transform_to_memory()
    assert len(td.aggregation[0]['transformed_text']) > 0
