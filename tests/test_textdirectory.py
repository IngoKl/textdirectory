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


def test_iterator():
    """Test the iterator of TextDirectory."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files()
    files = [file for file in td]
    assert len(files) == 10
    print(files[0]['path'].resolve())
    assert 'Text_' in str(files[0]['path'].resolve())


def test_simpple_aggregations():
    """Test the simplest form of aggregation."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    assert len(td.aggregate_to_memory()) == 4179


def test_tabulation(capsys):
    """Test the tabulation."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.print_aggregation()
    out, err = capsys.readouterr()
    assert 'path' in out


def test_print_pipeline(capsys):
    """"Test the print_pipeline function."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_chars_outliers()
    td.print_pipeline()
    out, err = capsys.readouterr()
    assert 'filter_by_chars_outliers' in out


def test_transform_to_memory():
    """Test the in memory transformation."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.transform_to_memory()
    assert len(list(td.get_aggregation())[0]['transformed_text']) > 0
