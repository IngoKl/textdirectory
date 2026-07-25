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


def test_cli_version():
    """--version reports the package version."""
    import textdirectory

    runner = CliRunner()
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert textdirectory.__version__ in result.output


def test_cli_python_m_invocation():
    """python -m textdirectory works."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, '-m', 'textdirectory', '--help'],
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'Usage' in result.stdout


def test_cli_output_file(testdata_dir, tmp_path):
    """--output_file writes the aggregation to a file."""
    output_file = tmp_path / 'aggregated.txt'

    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', str(testdata_dir), '--output_file', str(output_file)])

    assert result.exit_code == 0
    assert 'Lorem' in output_file.read_text(encoding='utf8')


def test_cli_filters_chain(testdata_dir):
    """Chained filters with numeric arguments work from the CLI."""
    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        ['--directory', str(testdata_dir), '--filters', 'filter_by_min_tokens,5/filter_by_max_chars,600'],
    )
    assert result.exit_code == 0


def test_cli_filter_with_filesize_arg(testdata_dir):
    """Filesize filters work from the CLI (regression: string vs int comparison)."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', str(testdata_dir), '--filters', 'filter_by_max_filesize,1'])
    assert result.exit_code == 0
    assert 'condimentum' not in result.output  # the largest file was filtered out


def test_cli_transformations(testdata_dir):
    """Transformations, including repeated ones with arguments, work from the CLI."""
    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            '--directory',
            str(testdata_dir),
            '--transformations',
            'transformation_replace_string,Lorem,X/transformation_replace_string,Ipsum,Y',
        ],
    )
    assert result.exit_code == 0
    assert 'Lorem' not in result.output
    assert 'X Y' in result.output


def test_cli_unknown_filter_fails_cleanly(testdata_dir):
    """An unknown filter name produces a clean error and a non-zero exit code."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', str(testdata_dir), '--filters', 'filter_by_nonsense,1'])
    assert result.exit_code == 1
    assert 'not a valid filter' in result.output


def test_cli_bad_directory_fails_cleanly():
    """A missing directory produces a message and a non-zero exit code."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', 'no_such_directory_xyz'])
    assert result.exit_code == 1
    assert 'could not be found' in result.output


def test_cli_empty_directory_fails_cleanly(tmp_path):
    """A directory without matching files produces a hint and a non-zero exit code."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--directory', str(tmp_path)])
    assert result.exit_code == 1
    assert 'no files' in result.output
