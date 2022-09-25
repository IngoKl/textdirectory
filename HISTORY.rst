=======
History
=======


0.1.0 (2018-04-26)
==================

* Initial release
* First release on PyPI.

0.1.1 (2018-04-27)
==================

* added filter_by_chars_outliers
* added transformation_remove_nl

0.1.2 (2018-04-29)
==================
* added transformation_postag
* added transformation_usas_en_semtag
* added transformation_uppercase
* added filter_by_filename_contains
* added parameter support for transformations

0.1.3 (2018-04-30)
==================
* filter_by_random_sampling now has a "replacement" option
* changed from tabulate to an embedded function
* added transformation_remove_non_ascii
* added transformation_remove_non_alphanumerical
* added filter_by_similar_documents

0.1.4 (2018-04-02)
==================
* fixed an object mutation problem in the tabulate function

0.2.0 (2018-05-13)
==================
* added transform_to_memory() function
* added transformation_to_leetspeak() function
* added transformation_crude_spellchecker
* added filter_by_max_filesize
* added filter_by_min_filesize
* fixed a bug where load_files() would fail if there were no files

0.2.1 (2019-06-13)
==================
* added transformation_remove_stopwords
* added transformation_remove_htmltags
* fixed some minor bugs

0.2.2 (2019-06-13)
==================
* changed the data packaging

0.3.0 (2020-01-19)
==================
* added transformation_remove_weird_tokens
* added transformation_lemmatizer
* fixed some minor bugs
* added a function to revert applied filters
* added a function that prints the current pipeline
* added a function that clears all transformations
* added helper functions to list available filters and transformations
* fixed a bug in which ``tabulate_flat_list_of_dicts`` would fail if the dictionary was empty
* ``self.aggregation`` does not hold a copy of the files anymore but references to ``self.files``
* transformations relying on spaCy are now estimating a max_length based on available memory
* TextDirectory objects are now iterable

0.3.1 (2020-01-20)
==================
* added long_description_content_type to setup.py

0.3.2 (2021-01-10)
==================
* added transformation_expand_english_contractions
* fixed some minor bugs
* added __str__ method to TextDirectory
* added filename to __str__ output
* added `get_text` method

0.3.3 (2022-09-25)
==================
* added filter_by_filenames
* added filter_by_filename_not_contains
* added transform_to_files
* added transformation_eebop4_to_plaintext
* added transformation_replace_digits
* added transformation_ftfy
* added fast and skip_checkpoint options to load_files
* added __repr__ method to TextDirectory
* added examples
* upgraded to spaCy 3
* improved the test suite
* fixed some minor bugs
