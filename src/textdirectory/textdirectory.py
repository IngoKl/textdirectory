"""Main module."""

import difflib
import os
import random
import statistics
from collections.abc import Callable, Iterator
from functools import wraps
from pathlib import Path
from typing import Any

from tqdm import tqdm

from textdirectory import helpers, transformations


class TextDirectory:
    def __init__(
        self, directory: str | Path, encoding: str = 'utf8', autoload: bool = False, disable_tqdm: bool = False
    ) -> None:
        """
        :param directory: path to the text directory
        :type directory: str
        """

        self.directory = Path(directory)
        self.files: list[dict[str, Any]] = []
        self.filenames: list[str] = []
        self.aggregation: list[int] = []
        self.staged_transformations: list[list[Any]] = []
        self.applied_filters: list[str] = []
        self.aggregation_states: list[list[Any]] = []
        self.current_state = 0
        self.encoding = encoding
        self.iterator = 0
        self.disable_tqdm = disable_tqdm

        if not self.directory.exists():
            raise NotADirectoryError

        if autoload:
            self.load_files()

    def __iter__(self) -> 'TextDirectory':
        self.iterator = 0
        return self

    def __next__(self) -> dict[str, Any]:
        if self.iterator < len(self.aggregation):
            file = self.files[self.aggregation[self.iterator]]
            self.iterator += 1
            return file
        else:
            raise StopIteration()

    def __str__(self) -> str:
        aggregation = helpers.tabulate_flat_list_of_dicts(list(self.get_aggregation()))
        staged_transformations = self.staged_transformations

        return f'{aggregation}\nStaged Transformation: {staged_transformations}'

    def __repr__(self) -> str:
        return f'TextDirectory: {len(self.files)} files in {self.directory}.'

    def save_aggregation_state(self) -> None:
        """Saves the current self.aggregation state."""
        self.aggregation_states.append([list(self.aggregation), list(self.applied_filters)])
        self.current_state = len(self.aggregation_states)

    def load_aggregation_state(self, state: int = 0) -> None:
        """
        :param state: the state to go back to
        :type state: int
        """

        if state in range(len(self.aggregation_states)):
            aggregation: list[int] = []
            previous_aggregation = self.aggregation_states[state]
            for file_id in previous_aggregation[0]:
                aggregation.append(file_id)

            self.aggregation = aggregation
            self.applied_filters = previous_aggregation[1]
            self.current_state = state
        else:
            raise ValueError

    def get_aggregation(self) -> Iterator[dict[str, Any]]:
        """A generator that provides the current aggregation."""
        for file_id in self.aggregation:
            yield self.files[file_id]

    def set_aggregation(self, aggregation: list[dict[str, Any]]) -> None:
        """Set the aggregation."""
        # Files are looked up by identity; a linear search per file would be quadratic
        file_ids = {id(file): file_id for file_id, file in enumerate(self.files)}

        self.aggregation = []
        for file in tqdm(aggregation, disable=self.disable_tqdm):
            file_id = file_ids.get(id(file))
            if file_id is None:
                # Not one of our file records (e.g. a copy): fall back to an equality search
                file_id = self.files.index(file)

            self.aggregation.append(file_id)

    def _require_metadata(self, key: str) -> None:
        """Raise if the loaded files lack the metadata a filter depends on.

        :param key: the metadata key a filter needs (e.g. characters)
        :type key: str
        """
        if any(file[key] is False for file in self.get_aggregation()):
            raise ValueError(
                f"This filter needs the '{key}' metadata, which was not collected because the files "
                'were loaded with fast=True. Reload them with load_files(fast=False).'
            )

    def filter(filter: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[misc]
        """A wrapper for filters."""

        @wraps(filter)
        def filter_wrapper(*args: Any, **kwargs: Any) -> Any:
            self = args[0]
            self.applied_filters.append(filter.__name__)
            self.save_aggregation_state()
            return filter(*args, **kwargs)

        return filter_wrapper

    def get_file_length(self, path: Path) -> int:
        """
        :param path: path to a textfile
        :return: the files length in characters
        """
        with path.open(encoding=self.encoding, errors='ignore') as f:
            fr = f.read()
            return len(fr)

    def get_file_tokens(self, path: Path) -> int:
        """
        :param path: path to a textfile
        :return: the files length in tokens
        """
        with path.open(encoding=self.encoding, errors='ignore') as f:
            # Replace all line breaks with spaces
            fr = f.read().replace('\n', ' ')
            return len(helpers.simple_tokenizer(fr))

    def get_text(self, file_id: int) -> str:
        """
        :param file_id: the file_id in files
        :return: the (transformed) text of the given file
        """

        if self.files[file_id]['transformed_text']:
            return self.files[file_id]['transformed_text']
        else:
            with self.files[file_id]['path'].open(encoding=self.encoding, errors='ignore') as f:
                return f.read()

    def load_files(
        self,
        recursive: bool = True,
        sort: bool = True,
        filetype: str = 'txt',
        fast: bool = False,
        skip_checkpoint: bool = False,
    ) -> None:
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

            for file in tqdm(files, disable=self.disable_tqdm):
                file = Path(file)

                if fast:
                    file_with_meta = {
                        'path': file,
                        'filename': file.name,
                        'characters': False,
                        'tokens': False,
                        'transformed_text': False,
                    }
                else:
                    file_with_meta = {
                        'path': file,
                        'filename': file.name,
                        'characters': self.get_file_length(file),
                        'tokens': self.get_file_tokens(file),
                        'transformed_text': False,
                    }

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
    def filter_by_max_chars(self, max_chars: int = 100) -> None:
        """
        :param max_chars: the maximum number of characters a file can have
        :type max_chars: int
        :human_name: Maximum characters
        """

        self._require_metadata('characters')

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if file['characters'] <= int(max_chars):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_chars(self, min_chars: int = 100) -> None:
        """
        :param min_chars: the minimum number of characters a file can have
        :type min_chars: int
        :human_name: Minimum characters
        """

        self._require_metadata('characters')

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if file['characters'] >= int(min_chars):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_max_tokens(self, max_tokens: int = 100) -> None:
        """
        :param max_tokens: the maximum number of tokens a file can have
        :type max_tokens: int
        :human_name: Maximum tokens
        """

        self._require_metadata('tokens')

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if file['tokens'] <= int(max_tokens):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_tokens(self, min_tokens: int = 1) -> None:
        """
        :param min_tokens: the minimum number of tokens a file can have
        :type min_tokens: int
        :human_name: Minimum tokens
        """

        self._require_metadata('tokens')

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if file['tokens'] >= int(min_tokens):
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_contains(self, contains: str) -> None:
        """
        :param contains: A string that needs to be present in the file
        :type contains: str
        :human_name: Contains string
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            with open(file['path'], encoding=self.encoding, errors='ignore') as f:
                fr = f.read()
                if contains in fr:
                    new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_not_contains(self, not_contains: str) -> None:
        """
        :param not_contains: A string that is not allowed to be present in the file
        :type not_contains: str
        :human_name: Does not contain string
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            with open(file['path'], encoding=self.encoding, errors='ignore') as f:
                fr = f.read()
                if not_contains not in fr:
                    new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filename_not_contains(self, not_contains: str) -> None:
        """
        :param not_contains: A string that needs not to be present in the filename
        :type not_contains: str
        :human_name: Filename does not contain string
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if not_contains not in file['path'].name:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filename_contains(self, contains: str) -> None:
        """
        :param contains: A string that needs to be present in the filename
        :type contains: str
        :human_name: Filename contains string
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if contains in file['path'].name:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_filenames(self, filenames: list[str]) -> None:
        """
        :param filenames: A list of filenames to include
        :type filenames: list
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if file['filename'] in filenames:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_random_sampling(self, n: int | str, replace: bool = False) -> None:
        """
        :param n: the number of documents in the sample
        :type n: int
        :param replace: Should valued be replaced
        :type replace: bool
        :human_name: Random sampling
        """

        if replace:
            self.aggregation = random.choices(self.aggregation, k=int(n))
        else:
            self.aggregation = random.sample(self.aggregation, k=int(n))

    @filter
    def filter_by_chars_outliers(self, sigmas: int = 2) -> tuple[float, float, float, float]:
        """
        :param sigmas: The number of stds that qualifies an outlier.
        :type sigmas: int
        :human_name: Character outliers
        """

        self._require_metadata('characters')

        chars_list = [file['characters'] for file in self.get_aggregation()]
        std = statistics.pstdev(chars_list)
        mean = statistics.fmean(chars_list)
        min = round(mean - sigmas * std, 1)
        max = round(mean + sigmas * std, 1)

        self.filter_by_min_chars(min)
        self.filter_by_max_chars(max)

        return std, mean, min, max

    @filter
    def filter_by_max_filesize(self, max_kb: int = 100) -> None:
        """
        :param max_mb: The maximum number of kB a file is allowed to have.
        :type max_mb: int
        :human_name: Maximum filesize
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if os.stat(file['path']).st_size / 1024 <= max_kb:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_min_filesize(self, min_kb: int = 10) -> None:
        """
        :param max_mb: The minimum number of kB a file is allowed to have.
        :type max_mb: int
        :human_name: Minimum Filesize
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            if os.stat(file['path']).st_size / 1024 >= min_kb:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_similar_documents(self, reference_file: str | Path, threshold: float = 0.8) -> None:
        """
        :param reference_file: Path to the reference file
        :type reference_file: str
        :param threshold: A value between 0.0 and 1.0 indicating the max. difference between the file and the reference.
        :type threshold: float
        :human_name: Similar documents
        """

        if not 0.0 <= threshold <= 1.0:
            raise (ValueError)

        new_aggregation: list[dict[str, Any]] = []
        with open(reference_file, encoding=self.encoding, errors='ignore') as rf:
            reference = rf.read()
            for file in self.get_aggregation():
                with open(file['path'], encoding=self.encoding, errors='ignore') as ft:
                    target = ft.read()
                    d = difflib.SequenceMatcher(None, reference, target)
                    if d.ratio() >= threshold:
                        new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    @filter
    def filter_by_type_token_ratio(self, min_ttr: float = 0.0, max_ttr: float = 1.0) -> None:
        """
        :param min_ttr: The minimum TTR
        :type min_ttr: float
        :param max_ttr: The maximum TTR
        :type max_ttr: float
        :human_name: Type-Token Ratio
        """

        new_aggregation: list[dict[str, Any]] = []
        for file in self.get_aggregation():
            with open(file['path'], encoding=self.encoding, errors='ignore') as f:
                ttr = helpers.type_token_ratio(f.read())

            if min_ttr <= ttr <= max_ttr:
                new_aggregation.append(file)

        self.set_aggregation(new_aggregation)

    def stage_transformation(self, transformation: list[Any]) -> None:
        """
        :param transformation: the transformation that should be staged and its parameters
        :type transformation: list
        """

        available_transformations = helpers.get_available_transformations()

        if transformation[0] in available_transformations:
            self.staged_transformations.append(transformation)
        else:
            raise NameError(
                f'{transformation[0]!r} is not a valid transformation. Available: {available_transformations}'
            )

    def destage_transformation(self, transformation: list[Any]) -> None:
        """
        :param transformation: the transformation that should be de-staged and its parameters
        :type transformation: list
        """

        if transformation in self.staged_transformations:
            self.staged_transformations.remove(transformation)
            return

        for staged in self.staged_transformations:
            if staged[0] == transformation[0]:
                self.staged_transformations.remove(staged)
                return

        raise NameError(f'The transformation {transformation[0]!r} is not staged.')

    def run_transformations(self, text: str) -> str:
        """
        :param text: the text to run staged transformations on
        :type text: str
        :return: the transformed text
        """

        transformed_text = text

        for transformation, *args in self.staged_transformations:
            transformation_method = getattr(transformations, transformation)
            transformed_text = transformation_method(transformed_text, *args)

        return transformed_text

    def run_filters(self, filters: list[Any]) -> None:
        """
        :param filters: A list of tuples with filters and their arguments.
        :type filters: list
        """

        available_filters = helpers.get_available_filters()

        for filter, *args in filters:
            if filter not in available_filters:
                raise NameError(f'{filter!r} is not a valid filter. Available: {available_filters}')

            filter_method = getattr(self, filter)
            filter_method(*args)

    def transform_to_files(self, output_directory: str | Path) -> None:
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

    def transform_to_memory(self) -> None:
        """Runs all transformations and stores the transformed texts in memory."""
        for file in self.get_aggregation():
            with file['path'].open(encoding=self.encoding, errors='ignore') as f:
                text = self.run_transformations(f.read())
                file['transformed_text'] = text

    def clear_transformation(self) -> None:
        """Destage all transformations and clear memory."""
        self.staged_transformations = []
        for file in self.files:
            file['transformed_text'] = False

    def aggregate_to_file(self, filename: str | Path = 'aggregated.txt') -> None:
        """
        :param filename: the path/filename to write to
        :type filename: str
        """
        with open(filename, 'w', encoding=self.encoding) as aggregation_file:
            for file in self.get_aggregation():
                with file['path'].open(encoding=self.encoding, errors='ignore') as f:
                    text = self.run_transformations(f.read())
                    aggregation_file.write(text)

    def aggregate_to_memory(self) -> str:
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

    def print_aggregation(self) -> None:
        """Print the aggregated files as a table."""
        print(helpers.tabulate_flat_list_of_dicts(list(self.get_aggregation())))
        print(f'\nStaged Transformations: {self.staged_transformations}')

    def print_saved_states(self) -> None:
        """Print all saved states."""
        print('Saved States:')
        for i, state in enumerate(self.aggregation_states):
            print(f'[{i}] - {len(state[0])} files after applying {state[1]}')

    def print_pipeline(self) -> None:
        """Print the current pipeline."""
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
