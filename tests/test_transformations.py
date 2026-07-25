"""Tests for the individual transformations."""

import pytest
import responses

from textdirectory.transformations import (
    transformation_crude_spellchecker,
    transformation_eebop4_to_plaintext,
    transformation_ftfy,
    transformation_remove_htmltags,
    transformation_remove_non_alphanumerical,
    transformation_remove_non_ascii,
    transformation_remove_stopwords,
    transformation_remove_weird_tokens,
    transformation_replace_digits,
    transformation_to_leetspeak,
    transformation_usas_en_semtag,
)


def test_transformation_remove_nl(td):
    """Test the remove_nl transformation."""
    td.stage_transformation(['transformation_remove_nl'])
    assert '\n' not in td.aggregate_to_memory()


def test_transformation_remove_htmltags():
    """Test the remove htmltags transformation."""
    test_string = '<html><body>This <span id="1">is</span> a <em>test</em></body></html>'
    assert transformation_remove_htmltags(test_string) == 'This is a test'


def test_transformation_uppercase(td):
    """Test the uppercase transformation."""
    td.stage_transformation(['transformation_uppercase'])
    assert td.aggregate_to_memory().isupper()


def test_transformation_remove_non_ascii_hard():
    """Test the remove non-ascii transformation."""
    test_string = 'This is a @ test string ~ containing non-ascii characters such as 😁.'
    assert (
        transformation_remove_non_ascii(test_string)
        == 'This is a @ test string ~ containing non-ascii characters such as .'
    )


def test_transformation_remove_non_alphanumerical():
    """Test the remove non-alphanumerical transformation."""
    test_string = 'non-alphanumerical @ / - * .'
    assert transformation_remove_non_alphanumerical(test_string).strip() == 'nonalphanumerical'


def test_transformation_to_leetspeak():
    """Test the leetspeak transformation."""
    test_string = 'leetspeak'
    assert transformation_to_leetspeak(test_string) == '133tsp34k'


def test_transformation_crude_spellchecker():
    """Test the crude spellchecker transformation."""
    test_string = 'There are two spellling mistaces in here.'
    assert transformation_crude_spellchecker(test_string) == 'There are two spelling mistakes in here.'


@pytest.mark.nlp
def test_transformation_remove_weird_tokens():
    """Test the remove weird tokens transformation."""
    test_string = 'Hello ---;#aaa World!'
    assert transformation_remove_weird_tokens(test_string, remove_double_space=True) == 'Hello World!'


@pytest.mark.nlp
def test_transformation_remove_stopwords():
    """Test the remove stopwords transformation."""
    test_string = 'There is a house on the hill.'
    assert transformation_remove_stopwords(test_string) == 'There is house hill.'


@pytest.mark.nlp
def test_transformation_test_arguments(td):
    """Test whether we can pass arguments to transformations."""
    td.stage_transformation(
        ['transformation_remove_stopwords', 'internal', 'en', 'en_core_web_sm', 'dolor,dolore,dolores']
    )
    text = td.aggregate_to_memory()
    assert 'dolor' not in text


@pytest.mark.nlp
def test_transformation_postag(td):
    """Test the postag transformation."""
    td.stage_transformation(['transformation_postag'])
    assert 'NN' in td.aggregate_to_memory()


@pytest.mark.nlp
def test_transformation_lemmatize(td):
    """Test the lemmatize transformation."""
    td.stage_transformation(['transformation_lemmatize'])
    assert 'language be complicate' in td.aggregate_to_memory()


def test_transformation_expand_contrations(td):
    """Test the expand English contractions transformation."""
    td.stage_transformation(['transformation_expand_english_contractions'])
    aggregated = td.aggregate_to_memory()
    assert 'She is the one who flew to Mars.' in aggregated
    assert 'I will finish the spaceship in time.' in aggregated


def test_transformation_eebop4_to_plaintext():
    """Test the eebop4 to plaintext transformation."""
    text = '<TEXT><FRONT><DIV1 TYPE="title page"><P>Lorem</P><P>Ipsum</P></DIV1></FRONT></TEXT>'
    assert transformation_eebop4_to_plaintext(text).replace('\n', '').replace(' ', '') == 'LoremIpsum'


def test_transformation_replace_digits(td):
    """Test the replace digits transformation."""
    td.filter_by_filenames(['Text_B.txt'])
    td.stage_transformation(['transformation_replace_digits'])
    assert '%' in td.aggregate_to_memory()

    # Test alternative replacement
    assert transformation_replace_digits('123 \n 456', 'x') == 'xxx \n xxx'


def test_transformation_ftfy(td):
    """Test the ftfy transformation."""
    td.stage_transformation(['transformation_ftfy'])
    assert 'ipsum lacus nisl' in td.aggregate_to_memory()

    # ftfy example test
    assert (
        transformation_ftfy('The Mona Lisa doesnÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢t have eyebrows.')
        == "The Mona Lisa doesn't have eyebrows."
    )


def test_transformation_replace_string(td):
    """Test the replace_string transformation."""
    td.filter_by_filenames(['Text_D.txt'])
    td.stage_transformation(['transformation_replace_string', 'languages', 'X'])
    assert 'The X are complicated.' in td.aggregate_to_memory()


@responses.activate
def test_transformation_usas_en_semtag_mocked():
    """Test the USAS semtag transformation against a canned response (offline)."""
    responses.add(
        responses.POST,
        'http://ucrel-api.lancaster.ac.uk/cgi-bin/usas.pl',
        body='<html><body><pre>0000001 002 ----- ----- 0000003 010 NN1 Language Q3 #</pre></body></html>',
        status=200,
    )
    tagged_text = transformation_usas_en_semtag('Language')
    assert tagged_text == '0000001 002 ----- ----- 0000003 010 NN1 Language Q3'


@pytest.mark.network
def test_transformation_usas_en_semtag_live():
    """Test the USAS semtag transformation against the live UCREL service."""
    tagged_text = transformation_usas_en_semtag('Language')
    assert 'NN1' in tagged_text
    assert 'Language' in tagged_text
