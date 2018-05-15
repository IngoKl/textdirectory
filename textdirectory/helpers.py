# -*- coding: utf-8 -*-

"""Helpers module."""
import copy

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

