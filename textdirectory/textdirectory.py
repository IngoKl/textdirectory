# -*- coding: utf-8 -*-

"""Main module."""
import os
import sys
import difflib
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.abspath('..'))
from textdirectory import transformations
from textdirectory import helpers

class TextDirectory:
    def __init__(self, directory):
        """
        :param directory: path to the text directory
        :type directory: str
        """

        self.directory = Path(directory)
        self.files = []
        self.filenames = []
        self.aggregation = []
        self.staged_transformations = []

        if not self.directory.exists():
            raise NotADirectoryError

    def get_file_length(self, path):
        """
        :param path: path to a textfile
        :return: the files length in characters
        """
        with path.open() as f:
            fr = f.read()
            return len(fr)

    def get_file_tokens(self, path):
        """
        :param path: path to a textfile
        :return: the files length in tokens
        """
        with path.open() as f:
            # Replace all line breaks with spaces
            fr = f.read().replace('\n', ' ')
            return len(fr.split(' '))

    def load_files(self, recursive=True, sort=True, filetype='txt'):
        """
        :param recursive: recursive search
        :type recursive: bool
        :param sort: sort the files by name
        :type sort: bool
        :param filetype: filetype to look for (e.g. txt)
        :type filetype: str
        """

        if recursive:
            files = list(self.directory.glob('**/*.' + filetype))
        else:
            files = list(self.directory.glob('*.' + filetype))

        if sort:
            files.sort()

        for file in files:
            file_with_meta = {'path': file, 'characters': self.get_file_length(file),
                              'tokens': self.get_file_tokens(file)}
            self.files.append(file_with_meta)
            self.filenames.append(file.name)

        # Initial population of self.aggregation
        self.aggregation = self.files

    def filter_by_max_chars(self, max_chars=100):
        """
        :param max_chars: the maximum number of characters a file can have
        :type max_chars: int
        """

        new_aggregation = []
        for file in self.aggregation:
            if file['characters'] <= int(max_chars):
                new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_min_chars(self, min_chars=100):
        """
        :param min_chars: the minimum number of characters a file can have
        :type min_chars: int
        """

        new_aggregation = []
        for file in self.aggregation:
            if file['characters'] >= int(min_chars):
                new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_max_tokens(self, max_tokens=100):
        """
        :param max_tokens: the maximum number of tokens a file can have
        :type max_tokens: int
        """

        new_aggregation = []
        for file in self.aggregation:
            if file['tokens'] <= int(max_tokens):
                new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_min_tokens(self, min_tokens=1):
        """
        :param min_tokens: the minimum number of tokens a file can have
        :type min_tokens: int
        """

        new_aggregation = []
        for file in self.aggregation:
            if file['tokens'] >= int(min_tokens):
                new_aggregation.append(file)

        self.aggregation = new_aggregation


    def filter_by_contains(self, contains):
        """
        :param contains: A string that needs to be present in the file
        :type contains: str
        """

        new_aggregation = []
        for file in self.aggregation:
            with open(file['path'], 'r') as f:
                fr = f.read()
                if contains in fr:
                    new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_not_contains(self, not_contains):
        """
        :param not_contains: A string that is not allowed to be present in the file
        :type not_contains: str
        """

        new_aggregation = []
        for file in self.aggregation:
            with open(file['path'], 'r') as f:
                fr = f.read()
                if not_contains not in fr:
                    new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_filename_contains(self, contains):
        """
        :param contains: A string that needs to be present in the filename
        :type contains: str
        """

        new_aggregation = []
        for file in self.aggregation:
            if contains in file['path'].name:
                new_aggregation.append(file)

        self.aggregation = new_aggregation

    def filter_by_random_sampling(self, n, replace=False):
        """
        :param n: the number of documents in the sample
        :type n: int
        :param replace: Should valued be replaced
        :type replace: bool
        """

        self.aggregation = np.random.choice(self.aggregation, int(n), replace=replace)

    def filter_by_chars_outliers(self, sigmas=2):
        """
        :param sigmas: The number of stds that qualifies an outlier.
        :type sigmas: int
        """

        chars_list = [file['characters'] for file in self.aggregation]
        std = np.std(chars_list)
        mean = np.mean(chars_list)
        min = round(mean - sigmas * std, 1)
        max = round(mean + sigmas * std, 1)

        self.filter_by_min_chars(min)
        self.filter_by_max_chars(max)

        return(std, mean, min, max)

    def filter_by_similar_documents(self, reference_file, threshold=0.8):
        """
        :param reference_file: Path to the reference file
        :type reference_file: str
        :param threshold: A value between 0.0 and 1.0 indicating the max. difference between the file and the reference.
        :type threshold: float
        """

        if not 0.0 <= threshold <= 1.0:
            raise(ValueError)

        new_aggregation = []
        with open(reference_file, 'r') as rf:
            reference = rf.read()
            for file in self.aggregation:
                with open(file['path'], 'r') as ft:
                    target = ft.read()
                    d = difflib.SequenceMatcher(None, reference, target)
                    if d.ratio() >= threshold:
                        new_aggregation.append(file)

        self.aggregation = new_aggregation

    def stage_transformation(self, transformation):
        """
        :param transformation: the transformation that should be staged and its parameters
        :type transformation: list
        """

        available_transformations = dir(transformations)

        if transformation[0] in available_transformations:
            self.staged_transformations.append(transformation)
        else:
            raise NameError


    def run_transformations(self, text):
        """
        :param text: the text to run staged transformations on
        :type text: str
        :return: the transformed text
        """

        transformed_text = text

        for transformation in self.staged_transformations:
            transformation_method = getattr(transformations, transformation[0])
            transformed_text = transformation_method(transformed_text, *transformation[1:])

        return transformed_text


    def run_filters(self, filters):
        """
        :param filters: A list of tuples with filters and their arguments.
        :type filters: list
        """

        for filter, *args in filters:
            filter_method = getattr(self, filter)
            filter_method(*args)

    def aggregate_to_memory(self):
        """
        :return: a string containing the aggregated text files
        :type: str
        """

        aggregated_string = ''
        for file in self.aggregation:
            with file['path'].open() as f:
                text = self.run_transformations(f.read())
                aggregated_string = aggregated_string + text

        return aggregated_string


    def aggregate_to_file(self, filename='aggregated.txt'):
        """
        :param filename: the path/filename to write to
        :type filename: str
        """
        with open(filename, 'w') as aggregation_file:
            for file in self.aggregation:
                with file['path'].open() as f:
                    text = self.run_transformations(f.read())
                    aggregation_file.write(text)


    def print_aggregation(self):
        """ Prints the aggregated files as a table. """
        print(helpers.tabulate_flat_list_of_dicts(self.aggregation))
        print(f'\nStaged Transformations: {self.staged_transformations}')
