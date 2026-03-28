Release draft for `0.1.1`

Summary
-------

- Interactive CLI: `binarybyte interactive` for guided, non-technical use.
- Eval enhancements: `--git-range` to evaluate git diffs directly.
- Plugin system: load deploy adapters from `.binarybyte/plugins/*.py`.
- Example plugin and docs added.

Publishing steps
----------------

1. Confirm `pyproject.toml` `version` is correct (now `0.1.1`).
2. Build distributions: `python -m build` (done).
3. Upload with twine: `python -m twine upload dist/*` (use TestPyPI first if desired).
4. Tag the release in git and push tags:

```bash
git add pyproject.toml CHANGELOG.md CHANGELOG.md README.md
git commit -m "chore: release 0.1.1"
git tag -a v0.1.1 -m "Release 0.1.1"
git push origin main --tags
```
