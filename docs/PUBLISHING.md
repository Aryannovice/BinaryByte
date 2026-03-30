Publishing BinaryByte to PyPI
=============================

This project uses `hatchling` (configured in `pyproject.toml`). These steps show how to build and publish a release to PyPI.

Prerequisites
- Python 3.11+
- `pip install build twine`
- A PyPI account

Build
-----

Run from the repository root:

```bash
python -m build
```

This produces artifacts in the `dist/` directory.

Publish
-------

Preferred: GitHub Actions + PyPI Trusted Publishing (OIDC)
---------------------------------------------------------

For open-source projects, prefer PyPI Trusted Publishing so you do not store a long-lived PyPI API token in GitHub.

High-level steps:

1. Configure your GitHub Actions workflow to use `pypa/gh-action-pypi-publish` with `id-token: write` permissions.
2. In PyPI, add the repository/workflow as a **Trusted Publisher** for the `binarybyte` project.
3. Push a version tag (e.g. `v0.3.0`) to trigger the release workflow.

Manual fallback: Twine upload
-----------------------------

If you prefer manual publishing, use `twine` to upload the built distributions.

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
