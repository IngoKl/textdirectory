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
    assert len(td.aggregate_to_memory()) == 89

