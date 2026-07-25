"""Tests for previously untested parts of the TextDirectory API."""

import subprocess
import sys

import pytest

from textdirectory.textdirectory import TextDirectory


def test_constructor_missing_directory_raises(tmp_path):
    """A non-existent directory raises immediately."""
    with pytest.raises(NotADirectoryError):
        TextDirectory(directory=tmp_path / 'does_not_exist')


def test_constructor_autoload(testdata_dir):
    """autoload=True loads the files on construction."""
    td = TextDirectory(directory=testdata_dir, autoload=True, disable_tqdm=True)
    assert len(td.aggregation) == 10


def test_repr_and_str(td):
    """__repr__ and __str__ describe the aggregation."""
    assert 'TextDirectory: 10 files' in repr(td)
    assert 'Staged Transformation' in str(td)


def test_get_text_from_disk(td):
    """get_text reads from disk when no transformed text exists."""
    text = td.get_text(0)
    assert len(text) > 0


def test_get_text_prefers_transformed(td):
    """get_text returns the transformed text when available."""
    td.stage_transformation(['transformation_uppercase'])
    td.transform_to_memory()

    assert td.get_text(0).isupper()


def test_run_filters_multiple(td):
    """run_filters applies a list of filters with arguments (the CLI path)."""
    td.run_filters([['filter_by_min_tokens', 5], ['filter_by_max_chars', 600]])

    assert len(td.aggregation) == 5
    assert 'filter_by_min_tokens' in td.applied_filters
    assert 'filter_by_max_chars' in td.applied_filters


def test_run_filters_rejects_unknown_names(td):
    """run_filters refuses non-filter method names (regression: unvalidated getattr)."""
    with pytest.raises(NameError):
        td.run_filters([['load_files']])


def test_load_files_nonrecursive(testdata_dir):
    """Non-recursive loading only picks up the top-level files."""
    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=False, filetype='txt')

    assert len(td.aggregation) == 5


def test_load_files_any_filetype(testdata_dir):
    """The '*' wildcard loads any file extension."""
    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=True, filetype='*')

    assert len(td.aggregation) == 10


def test_load_files_fast_skip_checkpoint(testdata_dir):
    """fast=True skips metadata; skip_checkpoint=True skips the initial state."""
    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=True, fast=True, skip_checkpoint=True)

    assert len(td.aggregation) == 10
    assert td.files[0]['characters'] is False
    assert td.files[0]['tokens'] is False
    assert td.aggregation_states == []


def test_metadata_filters_reject_fast_loaded_files(testdata_dir):
    """Filters needing metadata raise in fast mode (regression: silently kept every file)."""
    td = TextDirectory(directory=testdata_dir, disable_tqdm=True)
    td.load_files(recursive=True, filetype='txt', fast=True)

    for apply_filter in (
        lambda: td.filter_by_max_chars(1),
        lambda: td.filter_by_min_chars(1),
        lambda: td.filter_by_max_tokens(1),
        lambda: td.filter_by_min_tokens(1),
        lambda: td.filter_by_chars_outliers(1),
    ):
        with pytest.raises(ValueError, match='fast=True'):
            apply_filter()


def test_set_aggregation_accepts_equal_copies(td):
    """set_aggregation still resolves file records that are equal but not identical."""
    import copy

    td.set_aggregation([copy.deepcopy(file) for file in td.get_aggregation()])

    assert len(td.aggregation) == 10


def test_load_files_empty_directory_raises(tmp_path):
    """An existing but empty directory raises FileNotFoundError."""
    td = TextDirectory(directory=tmp_path, disable_tqdm=True)
    with pytest.raises(FileNotFoundError):
        td.load_files()


def test_transform_to_files_missing_directory_raises(td, tmp_path):
    """Writing to a non-existent output directory raises."""
    with pytest.raises(FileNotFoundError):
        td.transform_to_files(tmp_path / 'does_not_exist')


def test_import_has_no_side_effects():
    """Importing the package prints nothing and works from any directory."""
    result = subprocess.run(
        [sys.executable, '-c', 'import textdirectory'],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ''
