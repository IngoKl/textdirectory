# Releasing & Publishing

This page describes how to build the documentation and how to release a new version of *TextDirectory* to PyPI.

## Building the documentation

The documentation lives in `docs/` and is built with Sphinx (furo theme, Markdown via myst-parser).

Build it locally:

```bash
uv sync --group docs
uv run --group docs sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser to inspect the result. To treat warnings as errors (as a
pre-release check), add `-W`.

The hosted documentation at <https://textdirectory.readthedocs.io> is built automatically by Read the Docs on
every push, using `.readthedocs.yaml` (Python 3.12, `pip install .` plus `docs/requirements.txt`). If you change
the docs dependencies in `pyproject.toml`'s `docs` group, mirror the change in `docs/requirements.txt`.

## One-time setup for publishing

Releases are published to PyPI via **Trusted Publishing** (OIDC) — no API tokens or passwords are stored anywhere.

1. On PyPI, open the project's *Manage* → *Publishing* page and add a *Trusted Publisher*:
   * Owner: `IngoKl`, repository: `textdirectory`
   * Workflow name: `release.yml`
   * Environment name: `pypi`
2. On GitHub, create an environment named `pypi` (*Settings* → *Environments*). Optionally add yourself as a
   required reviewer — publishing will then wait for your approval.

## Release checklist

1. **Bump the version** in [`src/textdirectory/__init__.py`](https://github.com/IngoKl/textdirectory/blob/master/src/textdirectory/__init__.py)
   (`__version__ = 'X.Y.Z'`). This is the single source of truth; hatchling reads it at build time.

   Then refresh the editable install, otherwise `textdirectory --version` keeps reporting the previous version
   (it reads the installed metadata, not `__version__`, and `uv sync` alone does not rebuild it):

   ```bash
   uv sync --reinstall-package textdirectory
   ```

2. **Update `CHANGELOG.md`**: give the release a date and make sure all notable changes are listed.

3. **Run the full check suite**:

   ```bash
   uv run pytest              # includes the spaCy tests if the model is installed
   uv run pytest -m network   # optional: live-service tests (UCREL USAS)
   uv run ruff check src tests
   uv run mypy
   ```

4. **Build and verify the distribution**. `uv build` does not clean `dist/`, so remove it first — otherwise
   older releases are checked (and, in the manual path below, re-uploaded):

   ```bash
   rm -rf dist
   uv build
   uvx twine check dist/*
   ```

   Optionally, install the wheel into a scratch environment and smoke-test it:

   ```bash
   uv venv /tmp/td-check
   uv pip install --python /tmp/td-check dist/textdirectory-X.Y.Z-py3-none-any.whl
   /tmp/td-check/bin/textdirectory --version
   ```

5. **Commit, tag, and push**. Tags use the `vX.Y.Z` format:

   ```bash
   git commit -am "Release X.Y.Z"
   git tag vX.Y.Z
   git push && git push --tags
   ```

6. **The release workflow does the rest**: pushing a `v*` tag triggers
   [`.github/workflows/release.yml`](https://github.com/IngoKl/textdirectory/blob/master/.github/workflows/release.yml),
   which checks that the tag matches `__version__` and that the changelog is dated, runs the test suite, builds the
   sdist and wheel, runs `twine check`, and publishes to PyPI via Trusted Publishing.

7. **Verify the release**:
   * The new version appears on <https://pypi.org/project/textdirectory/>
   * `pip install textdirectory==X.Y.Z` works in a clean environment
   * Read the Docs built the new version (check the version switcher)
   * Create a GitHub Release from the tag and paste the changelog entry

## Manual publishing (fallback)

If the workflow is unavailable, you can publish manually with an API token:

```bash
uv build
uvx twine check dist/*
uvx twine upload dist/*
```

`twine upload` will prompt for a PyPI API token (username `__token__`).

## Rehearsing on TestPyPI

For risky changes to the packaging itself, rehearse against TestPyPI first:

```bash
uv build
uvx twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ textdirectory
```
