"""Sphinx configuration for textdirectory."""

from importlib.metadata import version as get_version

project = 'textdirectory'
author = 'Ingo Kleiber'
copyright = '2018-2026, Ingo Kleiber'

release = get_version('textdirectory')
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
