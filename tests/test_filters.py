"""Tests for the filters of TextDirectory."""


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
