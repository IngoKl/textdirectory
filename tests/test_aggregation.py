"""Tests for aggregating a TextDirectory to memory and to files."""


def expected_aggregate(testdata_dir):
    """Build the expected aggregate independently of TextDirectory internals."""
    files = sorted(testdata_dir.glob('**/*.txt'))
    return ''.join(f.read_text(encoding='utf8', errors='ignore') for f in files)


def test_simple_aggregation_memory(td, testdata_dir):
    """Test the simplest form of aggregation."""
    aggregated = td.aggregate_to_memory()

    assert 'languages' in aggregated
    assert aggregated == expected_aggregate(testdata_dir)


def test_simple_aggregation_file(td, tmp_path):
    """Test the simplest form of aggregation to a file."""
    output_file = tmp_path / 'output' / 'aggregated.txt'
    output_file.parent.mkdir(parents=True)

    td.aggregate_to_file(output_file)

    assert 'condimentum ultricies aliquam' in output_file.read_text()
