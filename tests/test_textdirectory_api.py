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


def test_nested_iteration_is_independent(td):
    """Two concurrent iterations do not share a cursor (regression: yielded 10 pairs, not 100)."""
    assert sum(1 for _a in td for _b in td) == 100


def test_iterator_yields_the_aggregation_not_all_files(td):
    """Iteration follows the aggregation, not the full file list."""
    td.filter_by_filenames(['Text_A.txt'])
    assert [file['filename'] for file in td] == ['Text_A.txt']


def test_transform_to_files_preserves_colliding_filenames(tmp_path):
    """Files sharing a name in different subdirectories do not overwrite each other."""
    source = tmp_path / 'input'
    (source / 'sub').mkdir(parents=True)
    (source / 'notes.txt').write_text('TOP LEVEL', encoding='utf8')
    (source / 'sub' / 'notes.txt').write_text('NESTED', encoding='utf8')

    output = tmp_path / 'output'
    output.mkdir()

    td = TextDirectory(directory=source, disable_tqdm=True)
    td.load_files(recursive=True, filetype='txt')
    td.transform_to_files(output)

    assert (output / 'notes.txt').read_text(encoding='utf8') == 'TOP LEVEL'
    assert (output / 'sub' / 'notes.txt').read_text(encoding='utf8') == 'NESTED'


def test_get_text_returns_empty_transformation_result(td):
    """An empty transformation result is returned instead of falling back to the file."""
    td.filter_by_filenames(['Text_B.txt'])
    td.stage_transformation(['transformation_replace_digits', ''])
    td.transform_to_memory()

    file_id = td.aggregation[0]
    assert td.files[file_id]['transformed_text'].strip() == ''
    assert td.get_text(file_id).strip() == ''


def test_exceptions_carry_messages(td, tmp_path):
    """User-facing errors explain what went wrong."""
    with pytest.raises(NotADirectoryError) as missing_dir:
        TextDirectory(directory=tmp_path / 'nope')
    assert str(missing_dir.value)

    with pytest.raises(ValueError) as bad_state:
        td.load_aggregation_state(99)
    assert str(bad_state.value)

    with pytest.raises(FileNotFoundError) as no_files:
        TextDirectory(directory=tmp_path, disable_tqdm=True).load_files()
    assert str(no_files.value)


def test_aggregate_to_memory_matches_aggregate_to_file(td, tmp_path):
    """Both output paths produce the same text."""
    td.filter_by_max_chars(600)
    td.stage_transformation(['transformation_lowercase'])

    output_file = tmp_path / 'aggregated.txt'
    td.aggregate_to_file(output_file)

    assert output_file.read_text(encoding='utf8') == td.aggregate_to_memory()


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
    with pytest.raises(NotADirectoryError):
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
