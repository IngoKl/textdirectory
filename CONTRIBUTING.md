# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Ways to Contribute

* **Report bugs** at <https://github.com/IngoKl/textdirectory/issues> — please include your operating system,
  Python version, and detailed steps to reproduce.
* **Fix bugs** or **implement features**: anything tagged `bug` or `enhancement` in the issue tracker is open to
  whoever wants to work on it.
* **Write documentation**: docstrings, the docs at <https://textdirectory.readthedocs.io>, or blog posts and
  articles elsewhere.
* **Submit feedback**: the easiest way is to file an issue at <https://github.com/IngoKl/textdirectory/issues>.

## Development Setup

The project uses [uv](https://docs.astral.sh/uv/) for environments and dependency management.

```bash
git clone https://github.com/<your-fork>/textdirectory.git
cd textdirectory

# Create the environment with dev tools and the optional NLP dependencies
uv sync --group dev --extra nlp
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

The spaCy model is not a declared dependency (it is not on PyPI), so a later plain `uv sync` removes it again.
Use `uv sync --inexact ...` to keep it, or reinstall the model afterwards — otherwise the tests that need it are
silently skipped.

Note: if you keep the repository inside a synced folder (e.g. Dropbox), exclude `.venv/` from syncing.

## Running Checks

```bash
uv run pytest              # test suite (tests hitting live services are excluded by default)
uv run pytest -m network   # live-service tests (UCREL USAS)
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
```

Tests that need spaCy and the `en_core_web_sm` model are skipped automatically when they are not installed.

## Pull Request Guidelines

1. Create a branch for your change and add tests for any new functionality or fixed bug.
2. Make sure the full check suite above passes locally.
3. Update the documentation if you add or change functionality (docstrings, README, and the docs pages).
4. Add an entry to `CHANGELOG.md` under the unreleased version.
5. The CI runs the tests on Python 3.10–3.13 on Linux and Windows; your change should pass on all of them.

## Releasing

See the [releasing documentation](https://textdirectory.readthedocs.io/en/latest/releasing.html) for how versions
are bumped, built, and published to PyPI.
