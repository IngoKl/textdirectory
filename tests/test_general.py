#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory


def test_iterator():
    """Test the iterator of TextDirectory."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files()
    files = [file for file in td]
    assert len(files) == 10
    print(files[0]['path'].resolve())
    assert 'Text_' in str(files[0]['path'].resolve())


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
