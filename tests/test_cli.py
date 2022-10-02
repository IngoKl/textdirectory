#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `textdirectory` package."""

import pytest
from click.testing import CliRunner

from textdirectory.textdirectory import TextDirectory
from textdirectory import cli


def test_cli_help():
    """Test the CLI help"""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert 'TextDirectory' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert 'Usage' in help_result.output


def test_cli_console_output():
    """Test the console outpu"""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', 'textdirectory/data/testdata/'])
    assert 'Lorem' in result.output