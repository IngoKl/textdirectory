# -*- coding: utf-8 -*-

"""Main module."""
import difflib
import os
import sys
from functools import wraps
from pathlib import Path

import numpy as np
from tqdm import tqdm

sys.path.insert(0, os.path.abspath('..'))
from textdirectory import transformations, helpers


class TextDirectory:
    def __init__(self, directory, encoding='utf8', autoload=False):
        """
        :param directory: path to the text directory
        :type directory: str
        """

        self.directory = Path(directory)
        self.files = []
        self.filenames = []
        self.aggregation = []
        self.staged_transformations = []
        self.applied_filters = []
        self.aggregation_states = []
        self.current_state = 0
        self.encoding = encoding
        self.iterator = 0

        if not self.directory.exists():
            raise NotADirectoryError

        if autoload:
            self.load_files()

    def __iter__(self):
        self.iterator = 0
        return self

    def __next__(self):
        if self.iterator < len(self.aggregation):
            file = self.files[self.aggregation[self.iterator]]
            self.iterator += 1
            return file
        else:
            raise StopIteration()

    def __str__(self):
        aggregation = helpers.tabulate_flat_list_of_dicts(list(self.get_aggregation()))
        staged_transformations = self.staged_transformations

        return f'{aggregation}\nStaged Transformation: {staged_transformations}'

    def __repr__(self):
        return f'TextDirectory: {len(self.files)} files in {self.directory}.'

    def save_aggregation_state(self):
        """Saves the current self.aggregation state."""
        current_state = []
        for file in self.get_aggregation():

            # A pointer would be great!
            current_state.append(self.files.index(file))

        self.aggregation_states.append([current_state, list(self.applied_filters)])
        self.current_state = len(self.aggregation_states)

    def load_aggregation_state(self, state=0):
        """
        :param state: the state to go back to
        :type state: int
        """

        if state in range(len(self.aggregation_states)):
            aggregation = []
            previous_aggregation = self.aggregation_states[state]
            for file_id in previous_aggregation[0]:
                aggregation.append(file_id)

            self.aggregation = aggregation
            self.applied_filters = previous_aggregation[1]
            self.current_state = state
        else:
            raise ValueError

    def get_aggregation(self):
        """A generator that provides the current aggregation."""
        for file_id in self.aggregation:
            yield self.files[file_id]

    def set_aggregation(self, aggregation):
        """Set the aggregation."""
        self.aggregation = []
        for file in tqdm(aggregation):
            self.aggregation.append(self.files.index(file))

    def filter(filter):
        """A wrapper for filters."""
        @wraps(filter)
        def filter_wrapper(*args, **kwargs):
            self = args[0]
            self.applied_filters.append(filter.__name__)
            self.save_aggregation_state()
            return filter(*args, **kwargs)

        return filter_wrapper

    def get_file_length(self, path):
        """
        :param path: path to a textfile
        :return: the files length in characters
        """
        with path.open(encoding=self.encoding, errors='ignore') as f:
            fr = f.read()
            return len(fr)

    def get_file_tokens(self, path):
        """
        :param path: path to a textfile
        :return: the files length in tokens
        """
        with path.open(encoding=self.encoding, errors='ignore') as f:
            # Replace all line breaks with spaces
            fr = f.read().replace('\n', ' ')
            return len(fr.split(' '))

    def get_text(self, file_id):
        """
        :param file_id: the file_id in files
        :return: the (transformed) text of the given file
        """

        if self.files[file_id]['transformed_text']:
            return self.files[file_id]['transformed_text']
        else:
            with self.files[file_id]['path'].open(encoding=self.encoding, errors='ignore') as f:
                return f.read()

    def load_files(self, recursive=True, sort=True, filetype='txt', fast=False, skip_checkpoint=False):
        """
        :param recursive: recursive search
        :type recursive: bool
        :param sort: sort the files by name
        :type sort: bool
        :param filetype: filetype to look for (e.g. txt)
        :type filetype: str
        :param fast: load files faster without getting metadata
        :type fast: bool
        """

        if recursive:
            if filetype == '*':
                files = list(self.directory.glob('**/*.*'))
            else:
                files = list(self.directory.glob('**/*.' + filetype))
        else:
            if filetype == '*':
                files = list(self.directory.glob('*.*'))
            else:
                files = list(self.directory.glob('*.' + filetype))

        if len(files) > 0:
            if sort:
                files.sort()

            for file in tqdm(files):
                file = Path(file)

                if fast:
                    file_with_meta = {'path': file, 'filename': file.name, 'characters': False,
                                    'tokens': False, 'transformed_text': False}
                else:
                    file_with_meta = {'path': file, 'filename': file.name, 'characters': self.get_file_length(file),
                                    'tokens': self.get_file_tokens(file), 'transformed_text': False}

                self.files.append(file_with_meta)
                self.filenames.append(file.name)

            # Initial population of self.aggregation
            self.set_aggregation(self.files)

            # Initial checkpoint
            if not skip_checkpoint:
                self.save_aggregation_state()
        else:
            raise FileNotFoundError

    @filter
    def filter_by_max_chars(self, max_chars=100):
        """
        :param max_chars: the maximum number of characters a file can have
        :type max_chars: int
        :human_name: Maximum characters
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if file['characters'] <= int(max_chars):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_chars(self, min_chars=100):
        """
        :param min_chars: the minimum number of characters a file can have
        :type min_chars: int
        :human_name: Minimum characters
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if file['characters'] >= int(min_chars):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_max_tokens(self, max_tokens=100):
        """
        :param max_tokens: the maximum number of tokens a file can have
        :type max_tokens: int
        :human_name: Maximum tokens
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if file['tokens'] <= int(max_tokens):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_tokens(self, min_tokens=1):
        """
        :param min_tokens: the minimum number of tokens a file can have
        :type min_tokens: int
        :human_name: Minimum tokens
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if file['tokens'] >= int(min_tokens):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_contains(self, contains):
        """
        :param contains: A string that needs to be present in the file
        :type contains: str
        :human_name: Contains string
        """

        new_aggregation = []
        for file in self.get_aggregation():
            with open(file['path'], 'r', encoding=self.encoding, errors='ignore') as f:
                fr = f.read()
                if contains in fr:
                    new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_not_contains(self, not_contains):
        """
        :param not_contains: A string that is not allowed to be present in the file
        :type not_contains: str
        :human_name: Does not contain string
        """

        new_aggregation = []
        for file in self.get_aggregation():
            with open(file['path'], 'r', encoding=self.encoding, errors='ignore') as f:
                fr = f.read()
                if not_contains not in fr:
                    new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filename_not_contains(self, not_contains):
        """
        :param not_contains: A string that needs not to be present in the filename
        :type not_contains: str
        :human_name: Filename does not contain string
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if not_contains not in file['path'].name:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filename_contains(self, contains):
        """
        :param contains: A string that needs to be present in the filename
        :type contains: str
        :human_name: Filename contains string
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if contains in file['path'].name:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filenames(self, filenames):
        """
        :param filenames: A list of filenames to include
        :type filenames: list
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if file['filename'] in filenames:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)


    @filter
    def filter_by_random_sampling(self, n, replace=False):
        """
        :param n: the number of documents in the sample
        :type n: int
        :param replace: Should valued be replaced
        :type replace: bool
        :human_name: Random sampling
        """

        self.aggregation = np.random.choice(self.aggregation, int(n), replace=replace)

    @filter
    def filter_by_chars_outliers(self, sigmas=2):
        """
        :param sigmas: The number of stds that qualifies an outlier.
        :type sigmas: int
        :human_name: Character outliers
        """

        chars_list = [file['characters'] for file in self.get_aggregation()]
        std = np.std(chars_list)
        mean = np.mean(chars_list)
        min = round(mean - sigmas * std, 1)
        max = round(mean + sigmas * std, 1)

        self.filter_by_min_chars(min)
        self.filter_by_max_chars(max)

        return std, mean, min, max

    @filter
    def filter_by_max_filesize(self, max_kb=100):
        """
        :param max_mb: The maximum number of kB a file is allowed to have.
        :type max_mb: int
        :human_name: Maximum filesize
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if os.stat(file['path']).st_size / 1024 <= max_kb:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_filesize(self, min_kb=10):
        """
        :param max_mb: The minimum number of kB a file is allowed to have.
        :type max_mb: int
        :human_name: Minimum Filesize
        """

        new_aggregation = []
        for file in self.get_aggregation():
            if os.stat(file['path']).st_size / 1024 >= min_kb:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_similar_documents(self, reference_file, threshold=0.8):
        """
        :param reference_file: Path to the reference file
        :type reference_file: str
        :param threshold: A value between 0.0 and 1.0 indicating the max. difference between the file and the reference.
        :type threshold: float
        :human_name: Similar documents
        """

        if not 0.0 <= threshold <= 1.0:
            raise(ValueError)

        new_aggregation = []
        with open(reference_file, 'r', encoding=self.encoding, errors='ignore') as rf:
            reference = rf.read()
            for file in self.get_aggregation():
                with open(file['path'], 'r', encoding=self.encoding, errors='ignore') as ft:
                    target = ft.read()
                    d = difflib.SequenceMatcher(None, reference, target)
                    if d.ratio() >= threshold:
                        new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

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

    def destage_transformation(self, transformation):
        """
        :param transformation: the transformation that should be de-staged and its parameters
        :type transformation: list
        """

        available_transformations = self.staged_transformations

        if transformation[0] in available_transformations:
            self.staged_transformations.remove(transformation)
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
        for file in self.get_aggregation():
            with file['path'].open(encoding=self.encoding, errors='ignore') as f:
                text = self.run_transformations(f.read())
                file['transformed_text'] = text
                aggregated_string = aggregated_string + text

        return aggregated_string

    def transform_to_memory(self):
        """Runs all transformations and stores the transformed texts in memory."""
        for file in self.get_aggregation():
            with file['path'].open(encoding=self.encoding, errors='ignore') as f:
                text = self.run_transformations(f.read())
                file['transformed_text'] = text


    def transform_to_files(self, output_directory):
        """
        Runs all transformations and stores the transformed texts in individual files.

        :param output_directory: the path/filename to write to
        :type output_directory: str
        """

        output_directory = Path(output_directory)

        if output_directory.is_dir():

            for file in self.get_aggregation():
                with file['path'].open(encoding=self.encoding, errors='ignore') as f:

                    with open(output_directory / file['filename'], 'w', encoding='utf8') as output_file:
                        output_file.write(self.run_transformations(f.read()))

        else:
            raise FileNotFoundError

    def clear_transformation(self):
        """Destage all transformations and clear memory."""
        self.staged_transformations = []
        for file in self.files:
            file['transformed_text'] = False

    def aggregate_to_file(self, filename='aggregated.txt'):
        """
        :param filename: the path/filename to write to
        :type filename: str
        """
        with open(filename, 'w', encoding=self.encoding, errors='ignore') as aggregation_file:
            for file in self.get_aggregation():
                with file['path'].open(encoding=self.encoding, errors='ignore') as f:
                    text = self.run_transformations(f.read())
                    aggregation_file.write(text)

    def print_aggregation(self):
        """Print the aggregated files as a table."""
        print(helpers.tabulate_flat_list_of_dicts(list(self.get_aggregation())))
        print(f'\nStaged Transformations: {self.staged_transformations}')

    def print_saved_states(self):
        """Print all saved states."""
        print('Saved States:')
        for i, state in enumerate(self.aggregation_states):
            print (f'[{i}] - {len(state[0])} files after applying {state[1]}')

    def print_pipeline(self):
        """Print the current pipeline. """
        print('Applied Filters:')
        if len(self.aggregation_states) > 0:
            print(f'> {len(self.aggregation_states)} states have been saved.')
            print(f'> Currently on state {self.current_state} / {len(self.aggregation_states)}')
        if len(self.applied_filters) == 0:
            print('None')
        else:
            for filter in self.applied_filters:
                print(filter)
        print('\nStaged Transformations:')
        if len(self.staged_transformations) == 0:
            print('None')
        else:
            for transformation in self.staged_transformations:
                print(transformation)
