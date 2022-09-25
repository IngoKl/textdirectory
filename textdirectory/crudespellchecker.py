# -*- coding: utf-8 -*-

"""Spellchecker module."""
import gzip
import os
import pickle
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


class CrudeSpellChecker():
    """A very simple and crude spellchecker based on Peter Norvig's design.
    Simple Language Models:
    crudesc_lm_en.gz.lm English based on COCA (sample), OANC (written), BNC
    crudesc_lm_ame.lm American English based on COCA (sample) and OANC (written)
    crudesc_lm_amehistorical.lm American English based on COHA (sample)
    """

    def __init__(self, caching=True, language_model='crudesc_lm_en'):
        """
        :param caching: caching of corrections
        :type caching: bool
        :param language_model: the name of the lm
        :type language_model: str
        """
        self.caching = caching
        self.cache = {}
        self.language_model_name = language_model

        model_path = Path(f'{os.path.join(os.path.dirname(__file__))}/data/language_models/'
                          f'{self.language_model_name}.gz.lm')
        print(model_path)
        with gzip.open(model_path, 'rb') as lm:
            self.frequencies = pickle.load(lm)

    def p_word(self, word):
        """
        :param word: a word
        :type word: str
        """
        return self.frequencies[word] / sum(self.frequencies.values())

    def correction(self, word):
        """
        :param word: a word
        :type word: str
        :return: most probable spelling correction for word
        """

        # Preserve
        word_isupper = word[0].isupper()
        word = word.lower()

        def reconstruct_case(word, word_isupper):
            """
            :param word: the word
            :type word: str
            :param word_isupper: the initial capitalization
            :type word_isupper: bool
            :return: the word with its initial capitalization
            """
            if word_isupper:
                return word.capitalize()
            else:
                return word

        if word in self.cache:
            return reconstruct_case(self.cache[word], word_isupper)
        else:
            correction = max(self.candidates(word), key=self.p_word)

            if self.caching:
                if correction not in self.cache:
                    self.cache[word] = correction

            return reconstruct_case(correction, word_isupper)

    def candidates(self, word):
        """
        :param word: a word
        :type word: str
        :return: a list of candidates
        """
        return (self.known([word]) or self.known(self.edit_distance_1(word)) or
                self.known(self.edit_distance_2(word)) or [word])

    def known(self, words):
        """
        :param word: a word
        :type word: str
        :return: a subset of words in the dictionary of frequencies
        """
        return set(w for w in words if w in self.frequencies)

    def edit_distance_1(self, word):
        """
        :param word: a word
        :type word: str
        :return: all edits one edit away from the word
        """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]

        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word):
        """
        :param word: a word
        :type word: str
        :return: all edits two edits away from the word
        """
        return (e2 for e1 in self.edit_distance_1(word) for e2 in self.edit_distance_1(e1))

    def correct_string(self, string, return_corrections=False):
        """
        :param string: the string to correct.
        :type string: str
        :param return_corrections: include the corrections in the result
        :type return_corrections: bool
        :return: the corrected string
        """
        corrections = []
        corrected = []
        for word in string.split():
            corrected_word = self.correction(re.findall(r'\w+', word)[0])
            corrected_word = re.sub(r'(.*?)(\w+)(.*?)', f'\g<1>{corrected_word}\g<3>', word)
            corrected.append(corrected_word)

            if return_corrections and corrected_word != word:
                corrections.append((word, corrected_word))

        if return_corrections:
            return (' '.join(corrected), corrections)
        else:
            return ' '.join(corrected)


def generate_crudespellchecker_lm(corpus_directory, model_name, strip_xml=False):
    """
    :param corpus_directory: path the folder containing the files.
    :type corpus_directory: str
    :param model_name: th name of the model
    :type model_name: str
    :param strip_xml: stripping XML tags with bs4
    :type strip_xml: bool
    """
    frequencies = Counter()
    files = list(Path(corpus_directory).glob('*.txt'))

    for file in files:
        with open(file, 'r', errors='ignore') as file:
            if strip_xml:
                soup = BeautifulSoup(file.read().lower(), 'lxml')
                text = soup.get_text()
            else:
                text = file.read().lower()

            file_frequency = Counter(re.findall(r'\b[^\d\W]+\b', text))
        frequencies = frequencies + file_frequency

    with gzip.open(model_name + '.gz.lm', 'wb') as pkl:
        pickle.dump(frequencies, pkl)

