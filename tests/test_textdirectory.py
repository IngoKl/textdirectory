#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory
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
    assert len(td.aggregate_to_memory()) == 681

def test_filter_by_chars_outliers():
    """Test the outlier filter."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_chars_outliers(1)
    assert len(td.aggregation) == 4

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

def test_transformation_postag():
    """Test the postag transformation."""
    td = TextDirectory(directory='data/testdata/')
    td.load_files(True, 'txt')
    td.stage_transformation(['transformation_postag'])
    assert 'NN' in td.aggregate_to_memory()
