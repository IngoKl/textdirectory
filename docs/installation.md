# Installation

## Stable release

Install *TextDirectory* from PyPI:

```bash
pip install textdirectory
```

This installs the core package. Python 3.10 or newer is required.

## Optional NLP features

The spaCy-based transformations (`transformation_postag`, `transformation_lemmatize`,
`transformation_remove_stopwords`, and `transformation_remove_weird_tokens`) require the optional `nlp` extra and
a spaCy model:

```bash
pip install 'textdirectory[nlp]'
python -m spacy download en_core_web_sm
```

Without the extra, the rest of the package works normally; calling a spaCy-based transformation raises an
`ImportError` explaining what to install.

## From source

```bash
git clone https://github.com/IngoKl/textdirectory.git
cd textdirectory
pip install .
```

Or, using [uv](https://docs.astral.sh/uv/) for development:

```bash
uv sync --group dev --extra nlp
```
