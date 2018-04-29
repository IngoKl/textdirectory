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

.. csv-table::
   :header: "Version", "Filters", "Transformations"
   :widths: 10, 30, 30

   0.1.0, filter_by_max_chars(n); filter_by_min_chars(n); filter_by_max_tokens(n); filter_by_min_tokens(n); filter_by_contains(str); filter_by_not_contains(str); filter_by_random_sampling(n), transformation_lowercase
   0.1.1, filter_by_chars_outliers(n sigmas), transformation_remove_nl
   0.1.2, filter_by_filename_contains(str), transformation_usas_en_semtag; transformation_uppercase; transformation_postag(spaCy model)

Quickstart
----------
Install *TextDirectory* via pip: ``pip install textdirectory``

*TextDirectory*, as exemplified below, works with a two-stage model. After loading in your data (directory) you can iteratively select the files you want to process. In a second step you can perform transformations on the text before finally aggregating it.

.. image:: https://user-images.githubusercontent.com/16179317/39367589-7f774116-4a37-11e8-9a09-5cbdf5f3311b.png
        :alt: TextDirectory

As a Command-Line Tool
~~~~~~~~~~~~~~~~~~~~~~
*TextDirectory* comes equipped with a CLI.

The syntax for both the *filters* and *tranformations* works similarly. They are chained by adding slashes (/) and
parameters are passed via commas (,): ``filter_by_min_tokens,5/filter_by_random_sampling,2``.

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
    td.stage_transformation(['transform_lowercase'])
    td.aggregate_to_file('aggregated.txt')

If we wanted to keep working with the actual aggregated text, we could have called ``text = td.aggregate_to_memory()``.

ToDo
--------
* Increasing test coverage
* Writing better documentation
* Adding better error handling (raw exception are, well ...)
* Adding logging

Behaviour
---------
We are not holding the actual texts in memory. This leads to much more disk read activity (and time inefficiency), but
saves memory.

``transformation_usas_en_semtag`` relies on the web versionof `Paul Rayson's USAS Tagger
<http://ucrel.lancs.ac.uk/usas/>`_. Don't use this transformation for large amounts of text, give credit, and
consider using their commercial product `Wmatrix <http://ucrel.lancs.ac.uk/wmatrix/>`_.


Credits
-------
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
