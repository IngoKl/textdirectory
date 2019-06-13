# -*- coding: utf-8 -*-

"""Transformation module."""
import sys
import os
import html
import requests
import spacy
from bs4 import BeautifulSoup
import re
from pathlib import Path

sys.path.insert(0, os.path.abspath('..'))
from textdirectory.crudespellchecker import CrudeSpellChecker


def transformation_postag(text, spacy_model='en_core_web_sm', *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :return: the transformed text
    :type return: str
    """

    nlp = spacy.load(spacy_model)
    doc = nlp(text)

    transformed_text = ''
    for token in doc:
        # This handles most linebreaks, etc.
        if len(token) > 1:
            transformed_text = f'{transformed_text} {token.text}_{token.tag_}'
        else:
            transformed_text = f'{transformed_text}{token.text}'

    return transformed_text


def transformation_remove_stopwords(text, stopwords_source='internal', stopwords='en', spacy_model='en_core_web_sm',
                                    custom_stopwords=None, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :param stopwords_source: [internal, file] where are stopwords loaded from
    :type stopwords_source: str
    :param stopwords: filename of a list containing stopwords
    :type stopwords: str
    :param spacy_model: the spaCy model we want to use
    :type spacy_model: str
    :param custom_stopwords: a list of additional stopwords to consider:
    :type custom_stopwords: str
    :return: the transformed text
    :type return: str
    """

    tokens = []
    transformed_text = ''

    nlp = spacy.load(spacy_model)
    nlp.max_length = 5000000
    doc = nlp(text, disable=['parser', 'tagger', 'ner', 'textcat'])

    # Locating the stopwords list
    if stopwords_source == 'internal':
        stopwords_path = Path(f'{os.path.join(os.path.dirname(__file__))}/data/stopwords/'
                              f'stopwords_{stopwords}.txt')
    if stopwords_source == 'file':
        stopwords_path = Path(stopwords)

    try:
        with open(stopwords_path, 'r') as stopwords_file:
            stopwords = stopwords_file.read().splitlines()[1:]
    except FileNotFoundError:
        return False

    if custom_stopwords:
        stopwords = stopwords + custom_stopwords.split(',')

    for token in doc:
        if token.text.lower() not in stopwords:
            tokens.append(token)

    # Detokenize
    for token in tokens:
        if token.whitespace_:
            transformed_text += token.text + ' '
        else:
            transformed_text += token.text

    return transformed_text


def transformation_uppercase(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.upper()


def transformation_lowercase(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.lower()


def transformation_remove_nl(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return text.replace('\n', ' ')


def transformation_usas_en_semtag(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    # Adhering to http://ucrel.lancs.ac.uk/claws/format.html
    text = html.escape(text)

    # Requesting USAS
    # USAS (web) is sensitive regarding the payload sequence
    payload = {'email': 'a.nobody@here.ac.uk', 'tagset': 'c7', 'style': 'horiz', 'text': text.strip()}
    r = requests.post('http://ucrel.lancs.ac.uk/cgi-bin/usas.pl', files=payload)

    # Parsing
    soup = BeautifulSoup(r.text, 'html.parser')
    tagged_text = soup.pre.text.strip()

    # Removing the last tag because USAS adds a hash as the last element
    tagged_text = tagged_text.split()
    tagged_text = ' '.join(tagged_text[:-1 or None])

    return tagged_text


def transformation_remove_non_ascii(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return ''.join(i for i in text if ord(i) < 128)


def transformation_remove_htmltags(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    return re.sub('<[^<]+?>', '', text)


def transformation_remove_non_alphanumerical(text, *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    pattern = re.compile('([^\s\w]|_)+')
    return pattern.sub('', text)


def transformation_to_leetspeak(text, *args):
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


def transformation_crude_spellchecker(text, language_model='crudesc_lm_en', *args):
    """
    :param text: the text to run the transformation on
    :type text: str
    :return: the transformed text
    :type return: str
    """

    cs = CrudeSpellChecker(language_model=language_model)
    transformed_text = cs.correct_string(text)

    return transformed_text
