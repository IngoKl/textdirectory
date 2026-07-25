"""Tests for the command-line interface."""

from click.testing import CliRunner

from textdirectory import cli


def test_cli_help():
    """Test the CLI welcome banner and help."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert 'TextDirectory' in result.output

    help_result = runner.invoke(cli.main, ['--help'])
    assert 'Usage' in help_result.output


def test_cli_console_output(testdata_dir):
    """Test aggregation to the console."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', str(testdata_dir)])
    assert result.exit_code == 0
    assert 'Lorem' in result.output
