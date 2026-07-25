"""Tests for the transformation pipeline (staging and running transformations)."""

import pytest


def test_transform_to_memory(td):
    """Test the in memory transformation."""
    td.transform_to_memory()
    assert len(list(td.get_aggregation())[0]['transformed_text']) > 0


def test_simple_transformation(td):
    """Test a simple transformation."""
    td.filter_by_filenames(['Text_E.txt'])
    td.stage_transformation(['transformation_lowercase'])
    td.stage_transformation(['transformation_uppercase'])

    td.transform_to_memory()
    assert 'THE ONE WHO FLEW TO MARS' in list(td.get_aggregation())[0]['transformed_text']


@pytest.mark.nlp
def test_complex_transformation(td):
    """Test a more complex transformation."""
    td.filter_by_filenames(['Text_E.txt'])
    td.stage_transformation(['transformation_remove_stopwords', 'internal', 'en', 'en_core_web_sm'])
    td.stage_transformation(['transformation_lemmatize', 'en_core_web_sm'])

    td.transform_to_memory()
    assert 'one fly Mars' in list(td.get_aggregation())[0]['transformed_text']


def test_destage_transformation(td):
    """Destaging removes exactly the requested transformation (regression: always raised)."""
    td.stage_transformation(['transformation_lowercase'])
    td.stage_transformation(['transformation_uppercase'])

    td.destage_transformation(['transformation_lowercase'])

    assert td.staged_transformations == [['transformation_uppercase']]


def test_destage_transformation_by_name(td):
    """Destaging by name removes a staged transformation with arguments."""
    td.stage_transformation(['transformation_replace_string', 'a', 'b'])

    td.destage_transformation(['transformation_replace_string'])

    assert td.staged_transformations == []


def test_destage_unknown_transformation_raises(td):
    """Destaging something that is not staged raises a NameError."""
    with pytest.raises(NameError):
        td.destage_transformation(['transformation_lowercase'])


def test_stage_transformation_rejects_non_transformations(td):
    """Only transformation_* callables can be staged (regression: any module attribute passed)."""
    for bogus in (['re'], ['html'], ['CrudeSpellChecker'], ['no_such_transformation']):
        with pytest.raises(NameError):
            td.stage_transformation(bogus)


def test_clear_transformation(td):
    """clear_transformation destages everything and clears transformed texts."""
    td.stage_transformation(['transformation_lowercase'])
    td.transform_to_memory()

    td.clear_transformation()

    assert td.staged_transformations == []
    assert all(file['transformed_text'] is False for file in td.files)


def test_transform_to_files(td, tmp_path):
    """Test transforming the aggregation to individual files."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    td.filter_by_filenames(['Text_A.txt', 'Text_C.txt'])
    td.stage_transformation(['transformation_lowercase'])
    td.transform_to_files(output_dir)

    assert 'stu' in (output_dir / 'Text_A.txt').read_text()
    assert 'ipsum' in (output_dir / 'Text_C.txt').read_text()
