# Changelog

## 0.4.1 (XXXX-XX-XX)

* the language model of the crude spellchecker is now restricted to the models shipped with the package; any other name could load (and execute) an arbitrary pickled file
* transformation_eebop4_to_plaintext no longer resolves external XML entities, which could be used to read local files; the lxml requirement is now >=5.0
* fixed CrudeSpellChecker.correct_string repeating the first correction across a token (`don't` became `don'don`, `well-known` became `well-well`)
* fixed transformation_lemmatize corrupting unrelated words (`I saw a sawmill.` became `I see a seemill.`); the text is now rebuilt from tokens
* fixed transformation_postag gluing single-character tokens onto the previous tag (`and_CCa girl_NNI`)
* fixed count_non_alphanum counting digits as non-alphanumeric, which made transformation_remove_weird_tokens delete every multi-digit number
* fixed transformation_expand_english_contractions matching inside words (`Porsche's` became `Porsche is`), ignoring capitalized forms (`Don't`, `He's`), and a typo that stopped `aren't` from being expanded
* fixed transform_to_files overwriting files when two input files in different subdirectories share a filename; the directory structure is now mirrored
* fixed transform_to_files writing UTF-8 regardless of the configured encoding
* fixed filter_by_filenames matching by substring when given a single filename instead of a list
* fixed transformation_remove_stopwords skipping the first line of a user-supplied stopword file; comments and blank lines are ignored instead
* fixed transformation_remove_weird_tokens leaving the whitespace of removed tokens behind
* fixed get_text falling back to the file on disk when a transformation legitimately produced an empty string
* fixed CrudeSpellChecker lowercasing acronyms and proper nouns it did not correct (`USA` became `Usa`)
* fixed nested iteration over a TextDirectory sharing a single cursor
* checkpoints are now saved after a filter has run, so that they hold the files it selected and are labelled correctly; a filter that raises no longer records a state
* current_state is now always a valid state index, and loading a state no longer rewrites the state that was loaded
* saved states are now AggregationState named tuples; indexing them as `state[0]` / `state[1]` still works
* filters that need character or token metadata now raise a ValueError in fast mode instead of silently keeping every file
* transformation arguments passed on the command line are now coerced to the expected types, so boolean options can be switched off
* all exceptions raised for invalid input now carry a message
* aggregate_to_memory no longer builds the result by repeated concatenation, which was quadratic (2000 files: 1.2s to 0.14s)
* the crude spellchecker no longer recomputes the language model total for every candidate
* sped up set_aggregation and save_aggregation_state, which performed a linear search per file
* documented that transformation_usas_en_semtag uploads the text to a third-party server
* documented that `uv sync` removes the spaCy model unless `--inexact` is used
* the release workflow now checks the tag against the version, requires a dated changelog, and runs the tests before publishing

## 0.4.0 (2026-07-26)

* modernized the packaging: pyproject.toml + hatchling, src/ layout, uv-based development workflow
* supported Python versions are now 3.10–3.13
* made spaCy and psutil optional dependencies (`pip install 'textdirectory[nlp]'` plus `python -m spacy download en_core_web_sm`)
* dropped the numpy dependency (replaced by the standard library random and statistics modules)
* spaCy models are now loaded once and cached instead of being reloaded per file and transformation
* added type hints throughout the package (py.typed)
* added `--version` and `python -m textdirectory` support to the CLI
* CLI filter arguments are now coerced to the expected types (filesize, TTR, and similarity filters previously failed from the CLI)
* CLI errors now exit with a non-zero exit code
* replaced Travis CI with GitHub Actions; replaced the legacy Read the Docs configuration; rewrote the documentation in Markdown
* the test corpus is no longer shipped inside the wheel (moved to tests/data/testdata/)
* fixed destage_transformation, which could never destage anything
* fixed the CrudeSpellChecker correction cache (wrong cache key) and a crash on tokens without word characters
* fixed transformation_usas_en_semtag: HTTPS, request timeout, and raising on HTTP errors
* stage_transformation and run_filters now validate names against the actual registries
* fixed filter_by_random_sampling turning the aggregation into a numpy array; note that the random sequence differs from previous versions
* transformation_remove_stopwords now raises for an unknown source or missing stopwords file instead of returning False
* tabulate_flat_list_of_dicts returns '' for an empty list; type_token_ratio returns 0.0 for empty text
* aggregate_to_file no longer silently drops unencodable characters when writing

## 0.3.4 (2022-09-25)

* added transformation_replace_string
* added filter_by_type_token_ratio
* added tests for running transformations
* added contractions fix to transformation_lemmatize
* added the --disable_tqdm option to the CLI
* added the ability to output aggregations to the console when using the CLI
* added (static) coverage badge to the README
* unified some core approaches (e.g., how filters and transformations are applied; tokenizaton)
* improved test structure
* improved documentation
* fixed transformation_usas_en_semtag

## 0.3.3 (2022-09-25)

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

## 0.3.2 (2021-01-10)

* added transformation_expand_english_contractions
* fixed some minor bugs
* added __str__ method to TextDirectory
* added filename to __str__ output
* added `get_text` method

## 0.3.1 (2020-01-20)

* added long_description_content_type to setup.py

## 0.3.0 (2020-01-19)

* added transformation_remove_weird_tokens
* added transformation_lemmatizer
* fixed some minor bugs
* added a function to revert applied filters
* added a function that prints the current pipeline
* added a function that clears all transformations
* added helper functions to list available filters and transformations
* fixed a bug in which `tabulate_flat_list_of_dicts` would fail if the dictionary was empty
* `self.aggregation` does not hold a copy of the files anymore but references to `self.files`
* transformations relying on spaCy are now estimating a max_length based on available memory
* TextDirectory objects are now iterable

## 0.2.2 (2019-06-13)

* changed the data packaging

## 0.2.1 (2019-06-13)

* added transformation_remove_stopwords
* added transformation_remove_htmltags
* fixed some minor bugs

## 0.2.0 (2018-05-13)

* added transform_to_memory() function
* added transformation_to_leetspeak() function
* added transformation_crude_spellchecker
* added filter_by_max_filesize
* added filter_by_min_filesize
* fixed a bug where load_files() would fail if there were no files

## 0.1.4 (2018-05-02)

* fixed an object mutation problem in the tabulate function

## 0.1.3 (2018-04-30)

* filter_by_random_sampling now has a "replacement" option
* changed from tabulate to an embedded function
* added transformation_remove_non_ascii
* added transformation_remove_non_alphanumerical
* added filter_by_similar_documents

## 0.1.2 (2018-04-29)

* added transformation_postag
* added transformation_usas_en_semtag
* added transformation_uppercase
* added filter_by_filename_contains
* added parameter support for transformations

## 0.1.1 (2018-04-27)

* added filter_by_chars_outliers
* added transformation_remove_nl

## 0.1.0 (2018-04-26)

* Initial release
* First release on PyPI.
