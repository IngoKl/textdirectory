"""Tests for the filters of TextDirectory."""

import pytest


def filenames(td):
    """The filenames currently in the aggregation, sorted."""
    return sorted(file['filename'] for file in td.get_aggregation())


def test_filters_select_the_expected_files(td):
    """Filters keep the right files, not merely the right number of them."""
    td.filter_by_max_chars(50)
    assert filenames(td) == ['Text_2_A.txt', 'Text_A.txt', 'Text_B.txt', 'Text_C.txt', 'Text_D.txt']


def test_filter_by_contains_selects_the_expected_file(td):
    """The contains filter keeps exactly the matching file."""
    td.filter_by_contains('spaceship')
    assert filenames(td) == ['Text_E.txt']


def test_filter_by_filenames_matches_exactly(td):
    """A filename string is matched as a whole name, not as a substring."""
    td.filter_by_filenames('Text_A.txt')
    assert filenames(td) == ['Text_A.txt']


def test_filter_boundaries_are_inclusive(td):
    """The character filters include files sitting exactly on the boundary."""
    lengths = {file['filename']: file['characters'] for file in td.get_aggregation()}
    boundary = lengths['Text_A.txt']

    td.filter_by_max_chars(boundary)
    assert 'Text_A.txt' in filenames(td)

    td.load_aggregation_state(0)
    td.filter_by_min_chars(boundary)
    assert 'Text_A.txt' in filenames(td)


def test_filter_by_max_chars(td):
    """Test the max chars filter."""
    td.filter_by_max_chars(50)
    assert len(td.aggregation) == 5


def test_filter_by_min_chars(td):
    """Test the min chars filter."""
    td.filter_by_min_chars(500)
    assert len(td.aggregation) == 2


def test_filter_by_max_tokens(td):
    """Test the max tokens filter."""
    td.filter_by_max_tokens(4)
    assert len(td.aggregation) == 4


def test_filter_by_min_tokens(td):
    """Test the min tokens filter."""
    td.filter_by_min_tokens(100)
    assert len(td.aggregation) == 2


def test_filter_by_contains(td):
    """Test the contains filter."""
    td.filter_by_contains('spaceship')
    assert len(td.aggregation) == 1


def test_filter_by_not_contains(td):
    """Test the not contains filter."""
    td.filter_by_not_contains('spaceship')
    assert len(td.aggregation) == 9


def test_filter_by_random_sampling(td):
    """Test the random sampling filter."""
    td.filter_by_random_sampling(3)
    assert len(td.aggregation) == 3


def test_filter_by_random_sampling_returns_list(td):
    """Sampling keeps the aggregation a plain list (regression: became a numpy array)."""
    td.filter_by_random_sampling(3)

    assert isinstance(td.aggregation, list)

    # Follow-up filters and state saving keep working on the sampled aggregation
    td.filter_by_max_chars(10**9)
    td.save_aggregation_state()
    assert len(td.aggregation) == 3


def test_filter_by_random_sampling_with_replacement(td):
    """Sampling with replacement can exceed the number of files."""
    td.filter_by_random_sampling(12, replace=True)

    assert len(td.aggregation) == 12


def test_filter_by_similar_documents_invalid_threshold_raises(td, testdata_dir):
    """A threshold outside [0, 1] raises a ValueError."""
    with pytest.raises(ValueError):
        td.filter_by_similar_documents(reference_file=testdata_dir / 'Text_A.txt', threshold=1.5)


def test_filter_by_chars_outliers(td):
    """Test the outlier filter."""
    td.filter_by_chars_outliers(1)
    assert len(td.aggregation) == 9


def test_filter_by_filenames(td):
    """Test the by filenames filter."""
    td.filter_by_filenames(['Text_A.txt'])
    assert len(td.aggregation) == 1


def test_filter_by_filename_contains(td):
    """Test the filename contains filter."""
    td.filter_by_filename_contains('Text_A')
    assert len(td.aggregation) == 1


def test_filter_by_filename_not_contains(td):
    """Test the filename not contains filter."""
    td.filter_by_filename_not_contains('Text_A')
    assert len(td.aggregation) == 9


def test_filter_by_similar_documents(td, testdata_dir):
    """Test the similarity filter."""
    reference_file = testdata_dir / 'level_2' / 'Text_2_B.txt'
    td.filter_by_similar_documents(reference_file=reference_file, threshold=0.7)
    assert len(td.aggregation) == 2


def test_filter_by_max_filesize(td):
    """Test the filesize (max) filter."""
    td.filter_by_max_filesize(max_kb=1)
    assert len(td.aggregation) == 9


def test_filter_by_min_filesize(td):
    """Test the filesize (min) filter."""
    td.filter_by_min_filesize(min_kb=2)
    assert len(td.aggregation) == 1


def test_filter_by_type_token_ratio(td):
    """Test the TTR filter."""
    td.filter_by_type_token_ratio(0.4, 0.8)
    assert len(td.aggregation) == 3
