#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory


def test_simple_aggregation_memory():
    """Test the simplest form of aggregation."""
    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    aggregated = td.aggregate_to_memory()

    assert 'languages' in aggregated
    assert len(aggregated) == 4179


def test_simple_aggregation_file(tmp_path):
    """Test the simplest form of aggregation to a file."""
    output_file = tmp_path / 'output' / 'aggregated.txt'
    output_file.parent.mkdir(parents=True)

    td = TextDirectory(directory='textdirectory/data/testdata/')
    td.load_files(True, 'txt')
    td.aggregate_to_file(output_file)

    assert 'condimentum ultricies aliquam' in output_file.read_text()
