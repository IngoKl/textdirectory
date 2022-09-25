#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory

def test_filter_by_max_chars():
    """Test the max chars filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_max_chars(50)
    assert len(td.aggregation) == 5


def test_filter_by_min_chars():
    """Test the min chars filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_min_chars(500)
    assert len(td.aggregation) == 2


def test_filter_by_max_tokens():
    """Test the max tokens filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_max_tokens(4)
    assert len(td.aggregation) == 1


def test_filter_by_min_tokens():
    """Test the min tokens filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_min_tokens(100)
    assert len(td.aggregation) == 2


def test_filter_by_contains():
    """Test the contains filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_contains('spaceship')
    assert len(td.aggregation) == 1


def test_filter_by_not_contains():
    """Test the not contains filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_not_contains('spaceship')
    assert len(td.aggregation) == 9


def test_filter_by_random_sampling():
    """Test the random sampling filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_random_sampling(3)
    assert len(td.aggregation) == 3


def test_filter_by_chars_outliers():
    """Test the outlier filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_chars_outliers(1)
    assert len(td.aggregation) == 9


def test_filter_by_filenames():
    """Test the by filenames filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_filenames(['Text_A.txt'])
    print(td)
    assert len(td.aggregation) == 1


def test_filter_by_filename_contains():
    """Test the filename contains filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_filename_contains('Text_A')
    assert len(td.aggregation) == 1


def test_filter_by_filename_not_contains():
    """Test the filename not contains filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_filename_not_contains('Text_A')
    assert len(td.aggregation) == 9


def test_filter_by_similar_documents():
    """Test the similarity filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_similar_documents(reference_file='textdirectory/data/testdata/level_2/Text_2_B.txt', threshold=0.7)
    assert len(td.aggregation) == 2


def test_filter_by_max_filesize():
    """Test the filesize (max) filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_max_filesize(max_kb=1)
    assert len(td.aggregation) == 9


def test_filter_by_min_filesize():
    """Test the filesize (min) filter."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.filter_by_min_filesize(min_kb=2)
    assert len(td.aggregation) == 1
