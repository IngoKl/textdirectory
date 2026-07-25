"""Top-level package for textdirectory."""

__author__ = 'Ingo Kleiber'
__email__ = 'ingo@kleiber.me'
__version__ = '0.4.1'

from textdirectory import helpers, transformations
from textdirectory.crudespellchecker import CrudeSpellChecker
from textdirectory.textdirectory import TextDirectory

__all__ = ['CrudeSpellChecker', 'TextDirectory', '__version__', 'helpers', 'transformations']
