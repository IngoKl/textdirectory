#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory
from textdirectory.transformations import transformation_remove_non_ascii, transformation_remove_non_alphanumerical
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
    assert len(td.aggregate_to_memory()) == 1653

def test_filter_by_chars_outliers():
    """Test the outlier filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_chars_outliers(1)
    assert len(td.aggregation) == 4

def test_filter_by_similar_documents():
    """Test the similarity filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_similar_documents(reference_file='data/testdata/level_2/Text_E.txt', threshold=0.7)
    assert len(td.aggregation) == 2

def test_transformation_remove_nl():
    """Test the remove_nl transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_remove_nl'])
    assert '\n' not in td.aggregate_to_memory()

def test_transformation_uppercase():
    """Test the uppercase transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_uppercase'])
    assert td.aggregate_to_memory().isupper()

def test_transformation_remove_non_ascii():
    """Test the remove non-ascii transformation."""
    test_string = 'This is a @ test string ~ containing non-ascii characters such as 😁.'
    assert transformation_remove_non_ascii(test_string) == 'This is a @ test string ~ containing non-ascii characters such as .'

def test_transformation_remove_non_ascii():
    """Test the remove non-alphanumerical transformation."""
    test_string = 'non-alphanumerical @ / - * .'
    assert transformation_remove_non_alphanumerical(test_string).strip() == 'nonalphanumerical'

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
