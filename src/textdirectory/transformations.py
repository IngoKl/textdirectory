"""Transformation module."""

import html
import importlib.resources
import re
from pathlib import Path
from typing import Any

from textdirectory.crudespellchecker import CrudeSpellChecker
from textdirectory.helpers import count_non_alphanum, estimate_spacy_max_length

_SPACY_MODELS: dict[tuple[str, tuple[str, ...]], Any] = {}


def _load_spacy_model(model_name: str, disable: tuple[str, ...] = ()) -> Any:
    """Load and cache a spaCy model; raise a helpful error when the nlp extra is missing.

    :param model_name: the name of the spaCy model (e.g. en_core_web_sm)
    :type model_name: str
    :param disable: pipeline components to disable
    :type disable: tuple
    :return: the loaded spaCy Language object
    """
    key = (model_name, tuple(disable))

    if key not in _SPACY_MODELS:
        try:
            import spacy
        except ImportError as e:
            raise ImportError(
                'This transformation requires spaCy, which is an optional dependency. '
                "Install it with: pip install 'textdirectory[nlp]' and download the model "
                f'with: python -m spacy download {model_name}'
            ) from e

        try:
            _SPACY_MODELS[key] = spacy.load(model_name, disable=list(disable))
        except OSError as e:
            raise OSError(
                f'The spaCy model {model_name!r} is not installed. Run: python -m spacy download {model_name}'
            ) from e

    return _SPACY_MODELS[key]


def transformation_postag(text: str, spacy_model: str = 'en_core_web_sm', *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :return: the transformed text
    :type return: str
    :human_name: Add pos-tags
    """

    nlp = _load_spacy_model(spacy_model)
    nlp.max_length = int(estimate_spacy_max_length())
    doc = nlp(text)

    transformed_text = ''
    for token in doc:
        # This handles most linebreaks, etc.
        if len(token) > 1:
            transformed_text = f'{transformed_text} {token.text}_{token.tag_}'
        else:
            transformed_text = f'{transformed_text}{token.text}'

    return transformed_text


def transformation_remove_stopwords(
    text: str,
    stopwords_source: str = 'internal',
    stopwords: str = 'en',
    spacy_model: str = 'en_core_web_sm',
    custom_stopwords: str | None = None,
    *args: Any,
) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :param stopwords_source: [internal, file] where are stopwords loaded from
    :type stopwords_source: str
    :param stopwords: filename of a list containing stopwords
    :type stopwords: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :param custom_stopwords: a comma separated list of additional stopwords to consider:
    :type custom_stopwords: str
    :return: the transformed text
    :type return: str
    """

    tokens: list[Any] = []
    transformed_text = ''

    # Locating the stopwords list
    stopwords_path: Any
    if stopwords_source == 'internal':
        stopwords_path = importlib.resources.files('textdirectory').joinpath(  # type: ignore[call-arg]
            'data', 'stopwords', f'stopwords_{stopwords}.txt'
        )
    elif stopwords_source == 'file':
        stopwords_path = Path(stopwords)
    else:
        raise ValueError(f"Unknown stopwords_source {stopwords_source!r}; expected 'internal' or 'file'.")

    try:
        with open(stopwords_path, encoding='utf-8') as stopwords_file:
            stopword_list = stopwords_file.read().splitlines()[1:]
    except FileNotFoundError as e:
        raise FileNotFoundError(f'The stopwords file {stopwords_path} could not be found.') from e

    if custom_stopwords:
        stopword_list = stopword_list + custom_stopwords.split(',')

    nlp = _load_spacy_model(spacy_model)
    nlp.max_length = 5000000
    doc = nlp(text, disable=['parser', 'tagger', 'ner', 'textcat', 'lemmatizer'])

    for token in doc:
        if token.text.lower() not in stopword_list:
            tokens.append(token)

    # Detokenize
    for token in tokens:
        if token.whitespace_:
            transformed_text += token.text + ' '
        else:
            transformed_text += token.text

    return transformed_text


def transformation_uppercase(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.upper()


def transformation_lowercase(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.lower()


def transformation_remove_nl(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    text = text.replace('\r\n', '').replace('\n', '')
    return text


def transformation_usas_en_semtag(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    import requests
    from bs4 import BeautifulSoup

    # Adhering to http://ucrel.lancs.ac.uk/claws/format.html
    text = html.escape(text)

    # Requesting USAS
    # USAS (web) is sensitive regarding the payload sequence

    usas_payload = {
        'email': 'a.nobody@here.ac.uk',
        'tagset': 'c7',
        'style': 'horiz',
        'type': 'web',
        'text': text.strip(),
    }
    usas_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'referer': 'https://ucrel-api.lancaster.ac.uk/usas/tagger.html',
    }
    usas_request = requests.post(
        'https://ucrel-api.lancaster.ac.uk/cgi-bin/usas.pl',
        files=usas_payload,
        headers=usas_headers,
        allow_redirects=True,
        timeout=(10, 120),
    )
    usas_request.raise_for_status()

    # Parsing
    soup = BeautifulSoup(usas_request.text, 'html.parser')
    tagged_text = soup.text.strip()

    # Removing the last tag because USAS adds a hash as the last element
    tagged_tokens = tagged_text.split()
    tagged_text = ' '.join(tagged_tokens[: -1 or None])

    return tagged_text


def transformation_remove_non_ascii(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return ''.join(i for i in text if ord(i) < 128)


def transformation_remove_htmltags(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return re.sub('<[^<]+?>', '', text)


def transformation_remove_non_alphanumerical(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    pattern = re.compile(r'([^\s\w]|_)+')
    return pattern.sub('', text)


def transformation_to_leetspeak(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    replacements = (('e', '3'), ('a', '4'), ('l', '1'), ('o', '0'))

    transformed_text = text
    for a, b in replacements:
        transformed_text = transformed_text.replace(a, b)

    return transformed_text


def transformation_crude_spellchecker(text: str, language_model: str = 'crudesc_lm_en', *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    cs = CrudeSpellChecker(language_model=language_model)
    transformed_text = cs.correct_string(text)

    return transformed_text


def transformation_remove_weird_tokens(
    text: str, spacy_model: str = 'en_core_web_sm', remove_double_space: bool = False, *args: Any
) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :param remove_double_space: remove duplicated spaces
    :type: remove_double_space: bool
    :return: the transformed text
    :type return: str
    """

    nlp = _load_spacy_model(spacy_model, disable=('parser', 'tagger', 'ner', 'lemmatizer'))
    nlp.max_length = int(estimate_spacy_max_length(tokenizer_only=True))
    doc = nlp(text)

    for token in doc:
        # More non-alphanum than alphanum
        if count_non_alphanum(token.text) > len(token.text) / 2 and len(token.text) > 1:
            text = text.replace(token.text, '')

        # Remove very long tokens (45 seems to be one of the longest words in major dictionaries)
        if len(token.text) > 45:
            text = text.replace(token.text, '')

    if remove_double_space:
        text = re.sub(' +', ' ', text)

    return text


def transformation_lemmatize(text: str, spacy_model: str = 'en_core_web_sm', *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :return: the transformed text
    :type return: str
    :human_name: Lemmatizer
    """

    nlp = _load_spacy_model(spacy_model, disable=('parser', 'ner'))
    nlp.max_length = int(estimate_spacy_max_length(tokenizer_only=True))
    doc = nlp(text)

    for token in doc:
        if token.text[0] == "'":  # Fix for contractions
            text = text.replace(token.text, f' {token.lemma_}')
        else:
            text = text.replace(token.text, str(token.lemma_))

    return text


def transformation_expand_english_contractions(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    # This list certainly is not complete. However, it covers some of the most common cases.
    contractions = [
        ("he's", 'he is'),
        ("she's", 'she is'),
        ("that's", 'that is'),
        ("'re", ' are'),
        ("'ll", ' will'),
        ("'ve", ' have'),
        ("'d", ' would'),
        ("don't", 'do not'),
        ("can't", 'cannot'),
        ("are't", 'are not'),
        ("couldn't", 'could not'),
        ("shouldn't", 'should not'),
        ("isn't", 'is not'),
        ("doesn't", 'does not'),
        ("wasn't", 'was not'),
        ("won't", 'will not'),
        ("weren't", 'were not'),
        ("ain't", 'am not'),
        ("let's", 'let us'),
        ("y'all", 'you all'),
    ]

    for contraction in contractions:
        text = text.replace(contraction[0], contraction[1])

    return text


def transformation_eebop4_to_plaintext(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    from lxml import etree

    transformed_text = ''

    root = etree.fromstring(text.encode())
    text_element = root.xpath('//TEXT')[0]

    for e in text_element.itertext():
        if e != '\n':
            transformed_text += ' ' + e

    return transformed_text


def transformation_replace_digits(text: str, replacement_character: str = '%', *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    transformed_text = ''

    for character in text:
        if character.isdigit():
            transformed_text += replacement_character
        else:
            transformed_text += character

    return transformed_text


def transformation_ftfy(text: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    import ftfy

    return ftfy.fix_text(text)


def transformation_replace_string(text: str, replace: str, replace_with: str, *args: Any) -> str:
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.replace(replace, replace_with)
