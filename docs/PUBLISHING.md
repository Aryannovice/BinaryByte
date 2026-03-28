Publishing BinaryByte to PyPI
=============================

This project uses `hatchling` (configured in `pyproject.toml`). These steps show how to build and publish a release to PyPI.

Prerequisites
- Python 3.11+
- `pip install build twine`
- A PyPI account and an API token

Build
-----

Run from the repository root:

```bash
python -m build
```

This produces artifacts in the `dist/` directory.

Publish
-------

Use `twine` to upload the built distributions. Prefer using an API token stored in `~/.pypirc` or via `TWINE_USERNAME`/`TWINE_PASSWORD` environment variables.

```bash
python -m twine upload dist/*
```

If you want to test on Test PyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Notes
-----
- Ensure `pyproject.toml` has the correct `project` metadata (name, version, description, authors).
- Add a long description by setting `readme = "README.md"` in `pyproject.toml` (already present).
- Tag releases in git and bump `version` in `pyproject.toml` before publishing.
