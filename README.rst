=============
TextDirectory
=============


.. image:: https://img.shields.io/pypi/v/textdirectory.svg
        :target: https://pypi.python.org/pypi/textdirectory

.. image:: https://img.shields.io/travis/IngoKl/textdirectory.svg
        :target: https://travis-ci.org/IngoKl/textdirectory

.. image:: https://readthedocs.org/projects/textdirectory/badge/?version=latest
        :target: https://textdirectory.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


TextDirectory allows you to combine multiple text files into one aggregated file. TextDirectory also supports matching
files for certain criteria and applying transformations to the aggregated text.

TextDirectory can be used as a mere tool (via the CLI) and as a Python library.

Everything TextDirectory does could be achieved in bash or PowerShell. However, there are certain
use-cases (e.g. when used as a library) in which it might be useful.


* Free software: MIT license
* Documentation: https://textdirectory.readthedocs.io.


Features
--------
* Aggregating multiple text files
* Matching based on length (character, tokens), content, and random sampling
* Transforming the aggregated text (e.g. transforming the text to lowercase)

ToDo
--------
* Increasing test coverage
* Writing better documentation

Behaviour
--------
We are not holding the actual texts in memory. This leads to much more disk read activity (and time inefficiency), but
saves memory.

Credits
-------
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
