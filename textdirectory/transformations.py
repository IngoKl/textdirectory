# -*- coding: utf-8 -*-

"""Transformation module."""

import html
import requests
import spacy
from bs4 import BeautifulSoup


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
