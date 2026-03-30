Release notes for `0.3.0`

Summary
-------

- Interactive CLI: `binarybyte interactive` for guided, non-technical use.
- Eval enhancements: `--git-range` to evaluate git diffs directly.
- Plugin system: load deploy adapters from `.binarybyte/plugins/*.py`.
- Example plugin and docs added.

Publishing steps
----------------

1. Confirm `pyproject.toml` `version` is correct (now `0.3.0`).
2. Run tests + lint: `pytest` and `ruff check .`
3. Build distributions: `python -m build`
4. Validate metadata: `python -m twine check dist/*`
5. Tag the release in git and push tags:

```bash
git add pyproject.toml CHANGELOG.md README.md docs/RELEASE_NOTES.md
git commit -m "chore: release 0.3.0"
git tag -a v0.3.0 -m "Release 0.3.0"
git push origin main --tags
```

If GitHub Actions is configured for PyPI Trusted Publishing (OIDC), pushing the tag will publish automatically.
