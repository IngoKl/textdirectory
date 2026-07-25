# Usage

*TextDirectory* works with a two-stage model: after loading your data (a directory of text files) you iteratively
select files by applying *filters*; then you stage *transformations* that are applied to the text when you finally
aggregate it to a file or to memory.

## As a Command-Line Tool

The CLI is available as `textdirectory` (or `python -m textdirectory`).

Filters and transformations are chained with slashes (`/`); parameters are passed with commas (`,`):

```bash
# Simple aggregation of all .txt files in testdata/
textdirectory --directory testdata --output_file aggregated.txt

# Any file extension instead of just .txt
textdirectory --directory testdata --output_file aggregated.txt --filetype *

# Filters and a transformation
textdirectory --directory testdata --output_file aggregated.txt \
    --filters filter_by_min_tokens,5/filter_by_random_sampling,2 \
    --transformations transformation_lowercase

# The same transformation staged twice with different arguments
textdirectory --directory testdata --output_file aggregated.txt \
    --transformations transformation_replace_string,lorem,x/transformation_replace_string,ipsum,y
```

If `--output_file` is omitted, the aggregated text is printed to the console. `--recursive True` searches
subdirectories; `--encoding` sets the file encoding (default `utf8`); `--disable_tqdm True` hides the progress bar.

Run `textdirectory --help` for the full list of options, including all available filters and transformations.

## As a Python Library

```python
import textdirectory

td = textdirectory.TextDirectory(directory='testdata')
td.load_files(recursive=False, filetype='txt', sort=True)
td.filter_by_min_tokens(5)
td.filter_by_random_sampling(2)
td.stage_transformation(['transformation_lowercase'])
td.aggregate_to_file('aggregated.txt')
```

With `autoload=True` the files are loaded on construction; `aggregate_to_memory()` returns the aggregated text as
a string instead of writing a file:

```python
td = textdirectory.TextDirectory(directory='testdata', autoload=True)
text = td.aggregate_to_memory()
```

`get_text(file_id)` returns the (transformed, if available) text of a single file.

### States (checkpoints)

Every applied filter creates a *state*. `td.print_saved_states()` lists them, and
`td.load_aggregation_state(state=0)` restores a previous one.

### Transformation arguments

Arguments are passed positionally in the staged list:

```python
# transformation_remove_stopwords(text, stopwords_source='internal', stopwords='en', spacy_model='en_core_web_sm', custom_stopwords=None)
td.stage_transformation(['transformation_remove_stopwords', 'internal', 'en', 'en_core_web_sm', 'dolor'])
```

### Transforming to files

Instead of aggregating, filtered and transformed texts can be written back to individual files:

```python
td = textdirectory.TextDirectory(directory='input')
td.load_files()
td.filter_by_max_chars(480)
td.stage_transformation(['transformation_to_leetspeak'])
td.transform_to_files('output')
```

### Performance notes

Texts are not held in memory; every aggregation re-reads from disk (except after `aggregate_to_memory` /
`transform_to_memory`). For large directories, `load_files(fast=True, skip_checkpoint=True)` skips the metadata
collection — filters relying on that metadata (character and token counts) then raise a `ValueError`.

`transformation_usas_en_semtag` calls the web version of
[Paul Rayson's USAS tagger](http://ucrel.lancs.ac.uk/usas/). **It uploads the full text of every processed file to a
third-party server operated by Lancaster University — do not use it with confidential, personal, or licensed data.**
Don't use it for large amounts of text, give credit, and consider
[Wmatrix](http://ucrel.lancs.ac.uk/wmatrix/) for serious work.
