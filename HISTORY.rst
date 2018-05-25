=======
History
=======

0.1.0 (2018-04-26)
------------------

* Initial release
* First release on PyPI.

0.1.1 (2018-04-27)
------------------

* added filter_by_chars_outliers
* added transformation_remove_nl

0.1.2 (2018-04-29)
------------------
* added transformation_postag
* added transformation_usas_en_semtag
* added transformation_uppercase
* added filter_by_filename_contains
* added parameter support for transformations

0.1.3 (2018-04-30)
------------------
* filter_by_random_sampling now has a "replacement" option
* changed from tabulate to an embedded function
* added transformation_remove_non_ascii
* added transformation_remove_non_alphanumerical
* added filter_by_similar_documents

0.1.4 (2018-04-02)
------------------
* fixed an object mutation problem in the tabulate function

0.2.0 (2018-05-13)
------------------
* added the transform_to_memory() function
* added transformation_to_leetspeak
* added transformation_crude_spellchecker
* added filter_by_max_filesize
* added filter_by_min_filesize
* fixed a bug where load_files() would fail if there were no files

0.3.0 (2018-00-00)
------------------
* added transformation_remove_weird_tokens
* added a function to revert applied filters
* added a function that prints the current pipeline
* added a function that clears all transformations
* fixed a bug in which ``tabulate_flat_list_of_dicts`` would fail if the dictionary was empty
* ``self.aggregation`` does not hold a copy of the files anymore but references to ``self.files``
* transformations relying on spaCy are now estimating a max_length based on available memory
* TextDirectory objects are now iterable
