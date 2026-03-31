# Contributing

Thanks for contributing to BinaryByte!

## Quick links

- Issues: https://github.com/Aryannovice/BinaryByte/issues
- Repository: https://github.com/Aryannovice/BinaryByte

## Development setup

Requirements:

- Python 3.11+
- (Optional) Docker CLI if you want to run sandbox evaluation locally

Clone + install:

```bash
git clone https://github.com/Aryannovice/BinaryByte.git
cd BinaryByte

python -m venv .venv
# Windows PowerShell:
#   .\.venv\Scripts\Activate.ps1
# macOS/Linux:
#   source .venv/bin/activate

python -m pip install -U pip
pip install -e ".[dev]"
```

Run quality checks:

```bash
python -m ruff check .
python -m pytest -q
```

## What to work on

Great contributions include:

- New deploy targets (adapters)
- New evaluation checks
- Docs improvements and usage examples
- Bug fixes and test coverage improvements

## Project conventions

- Keep changes small and focused (one theme per PR).
- Prefer adding tests for behavior changes.
- Update docs/examples when you add flags, change outputs, or modify configs.
- Don’t commit project-specific `.binarybyte/` folders from your local machine.

## Adding a deploy adapter (high level)

- Implement an adapter that subclasses `BaseAdapter`.
- Ensure it writes deterministic output files for the target tool.
- Add docs/examples showing how to enable the target in `.binarybyte/config.yaml`.

## Adding an eval check (high level)

- Implement a check that examines the diff content and returns a structured result.
- Keep checks fast and deterministic (suitable for CI).
- Add tests that demonstrate pass/fail behavior.

## Pull requests

Before opening a PR:

- `python -m ruff check .`
- `python -m pytest -q`

PRs should include:

- A clear description of what changed and why
- Screenshots/logs if it affects CLI output
- Tests when practical

## Security

Please do not report security vulnerabilities via public GitHub issues.
Use private channels (see maintainer contacts in the README) to disclose responsibly.
