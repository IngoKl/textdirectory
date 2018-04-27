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
|
|
.. image:: https://user-images.githubusercontent.com/16179317/39367680-cd409a00-4a37-11e8-8d42-0bed5a4e814b.png
        :alt: TextDirectory

*TextDirectory* allows you to combine multiple text files into one aggregated file. TextDirectory also supports matching
files for certain criteria and applying transformations to the aggregated text.

*TextDirectory* can be used as a mere tool (via the CLI) and as a Python library.

Of course, everything *TextDirectory* does could be achieved in bash or PowerShell. However, there are certain
use-cases (e.g. when used as a library) in which it might be useful.


* Free software: MIT license
* Documentation: https://textdirectory.readthedocs.io.


Features
--------
* Aggregating multiple text files
* Matching based on length (character, tokens), content, and random sampling
* Transforming the aggregated text (e.g. transforming the text to lowercase)

Quickstart
----------
Install *TextDirectory* via pip: ``pip install textdirectory``

*TextDirectory*, as exemplified below, works with a two-stage model. After loading in your data (directory) you can iteratively select the files you want to process. In a second step you can perform transformations on the text before finally aggregating it.

.. image:: https://user-images.githubusercontent.com/16179317/39367589-7f774116-4a37-11e8-9a09-5cbdf5f3311b.png
        :alt: TextDirectory

As a Command-Line Tool
~~~~~~~~~~~~~~~~~~~~~~
*TextDirectory* comes equipped with a CLI. 

**Example 1: A Very Simple Aggregation**

``textdirectory --directory testdata --output_file aggregated.txt``

This will take all files (.txt) in *testdata* and then aggregates the files into a file called *aggregated.txt*.

**Example 2: Applying Filters and Transformations**

In this example we want to filter the files based on their token count, perform a random sampling and finally transform all text to lowercase.

``textdirectory --directory testdata --output_file aggregated.txt --filters filter_by_min_tokens,5/filter_by_random_sampling,2 --transformations transformation_lowercase``

After passing two filters (*filter_by_min_tokens* and *filter_by_random_sampling*) we've applied the *transform_lowercase* transformation. 

The resulting file will contain the content of two files that each have at least five tokens.

As a Python Library
~~~~~~~~~~~~~~~~~~~
In order to demonstrate *TextDirectory* as a Python library, we'll recreate the second example from above:

.. code:: python

    import textdirectory
    td = textdirectory.TextDirectory(directory='testdata')
    td.load_files(recursive=False, filetype='txt', sort=True)
    td.filter_by_min_tokens(5)
    td.filter_by_random_sampling(2)
    td.stage_transformation('transform_lowercase')
    td.aggregate_to_file('aggregated.txt')
        
If we wanted to keep working with the actual aggregated text, we could have called ``text = td.aggregate_to_memory()``.

ToDo
--------
* Increasing test coverage
* Writing better documentation

Behaviour
---------
We are not holding the actual texts in memory. This leads to much more disk read activity (and time inefficiency), but
saves memory.

Credits
-------
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
