# -*- coding: utf-8 -*-

"""Helpers module."""
import copy
import re

import psutil

from textdirectory import textdirectory, transformations


def tabulate_flat_list_of_dicts(list_of_dicts, max_length=25):
    """
    :param list_of_dicts: a list of dictionaries; each list is a row
    :type list_of_dicts: list
    :param max_length: the maximum length of a cell
    :type max_length: int
    :return: a table
    :type return: str
    """

    # Create a copy of the list to prevent object mutation
    list_of_dicts = copy.deepcopy(list_of_dicts)

    if len(list_of_dicts) == 0:
        return False

    # Enforce a maximum length
    if max_length:
        for row in list_of_dicts:
            for key, value in row.items():
                row[key] = str(value)[:max_length]

    # Determine the width of the columns
    longest_values = {}

    for key in list_of_dicts[0].keys():
        longest_values[key] = len(key)

    for row in list_of_dicts:
        for key, value in row.items():
            value = str(value)
            if key in longest_values:
                if len(value) > longest_values[key]:
                    longest_values[key] = len(value)
            else:
                longest_values[key] = len(value)

    # Line / len(longest_values) = additonal characters for pipes
    length = 0
    for key, value in longest_values.items():
        length += value

    line = '\n|' + '-' * (length + len(longest_values) - 1) + '|'

    # Header based on the first dictionary
    table = line + '\n|'
    for key in list_of_dicts[0].keys():
        table += f'{key}'.ljust(longest_values[key]) + '|'

    table += line

    # Rows
    for row in list_of_dicts:
        table += '\n|'
        for key, value in row.items():
            # Remove linebreaks
            value = value.replace('\n', '')
            table += str(value).ljust(longest_values[key]) + '|'

    table += line

    return table


def count_non_alphanum(string):
    """
    :param string: a string
    :type string: str
    :return: the number of non-alphanumeric characters in the string
    :type return: int
    """

    non_alphanum = 0
    for c in string:
        if not c.isalpha():
            non_alphanum += 1

    return non_alphanum


def chunk_text(string, chunk_size=50000):
    """
    :param string: a string
    :type string: str
    :param chunk_size: the max characters of one chunk
    :type chunk_size: int
    :return: a list of chunks
    :type return: list
    """

    chunks = [string[i:i + chunk_size] for i in range(0, len(string), chunk_size)]
    return chunks


def estimate_spacy_max_length(override=False, tokenizer_only=False):
    """Returns a somewhat sensible suggestions for max_length."""
    memory = psutil.virtual_memory()
    gb_available = memory.available / 1024 / 1024 / 1024

    # tagger, parser, ner 100,000 characters = 1 GB
    estimated_max_length = gb_available * 100000

    if tokenizer_only:
        estimated_max_length = estimated_max_length * 3

    if override:
        estimated_max_length = override

    return estimated_max_length


def get_human_from_docstring(doc):
    """
    :param doc: if True, also return the 'human name'
    :type doc: string
    :return: a dictionary of name_* keys/values from the docstring.
    :type return: dict
    """
    doc = doc.replace('    ', '')
    res = re.findall('human_(.*):(.*)', doc)

    return {k:v.strip() for (k,v) in res} 


def get_available_filters(get_human_name=False):
    """
    :param get_human_name: if True, also return the 'human name'
    :type get_human_name: bool
    :return: a list of functions; if get_human_name a list of tuples
    :type return: list
    """
    
    available_filters = [filter for filter in dir(textdirectory.TextDirectory) if 'filter_by' in filter]

    if get_human_name:
        available_filters_with_human = []
        for f in available_filters:
            doc = getattr(textdirectory.TextDirectory, f).__doc__
            human = get_human_from_docstring(doc)
            if 'name' in human:
                available_filters_with_human.append((f, human['name']))
            else:
                available_filters_with_human.append((f, f))

        available_filters = available_filters_with_human

    return available_filters


def get_available_transformations(get_human_name=False):
    """
    :param get_human_name: if True, also return the 'human name'
    :type string: bool
    :return: a list of functions; if get_human_name a list of tuples
    :type return: list
    """

    available_transformations = [transformation for transformation in dir(transformations) if 'transformation' in transformation]

    if get_human_name:
        available_transformations_with_human = []
        for t in available_transformations:
            doc = getattr(textdirectory.transformations, t).__doc__
            human = get_human_from_docstring(doc)
            if 'name' in human:
                available_transformations_with_human.append((t, human['name']))
            else:
                available_transformations_with_human.append((t, t))

        available_transformations = available_transformations_with_human

    return available_transformations
