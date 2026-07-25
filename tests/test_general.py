"""General tests for the TextDirectory class."""


def test_iterator(td):
    """Test the iterator of TextDirectory."""
    files = list(td)
    assert len(files) == 10
    assert 'Text_' in str(files[0]['path'].resolve())


def test_tabulation(td, capsys):
    """Test the tabulation."""
    td.print_aggregation()
    out, err = capsys.readouterr()
    assert 'path' in out


def test_print_pipeline(td, capsys):
    """Test the print_pipeline function."""
    td.filter_by_chars_outliers()
    td.print_pipeline()
    out, err = capsys.readouterr()
    assert 'filter_by_chars_outliers' in out
