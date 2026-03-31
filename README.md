# BinaryByte

[![CI](https://github.com/Aryannovice/BinaryByte/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryannovice/BinaryByte/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/binarybyte.svg)](https://pypi.org/project/binarybyte/)
[![Python](https://img.shields.io/pypi/pyversions/binarybyte.svg)](https://pypi.org/project/binarybyte/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**BinaryByte is CI/CD for AI coding agents**: evaluate agent-proposed diffs, version shared agent state, and deploy verified rules to multiple targets (Cursor, Gemini CLI, Claude Code, Windsurf, Copilot, plus plugins).

**Current version:** 0.3.0

---

## Why BinaryByte

When you switch between editors and agents, rules and context drift. It’s also easy to merge risky diffs.

BinaryByte gives you:

- **Eval** — run checks on a patch file or a `git diff` range; write a **verdict** + a **state snapshot** per version label.
- **State** — keep one canonical `state.yaml` (memory + conventions) that can be deployed everywhere.
- **Deploy (gated)** — render that state into each tool’s native file format **only if** the chosen version’s verdict **passed**.

---

## Quickstart (60 seconds)

```bash
pip install binarybyte
binarybyte init .
binarybyte state add --key "stack" --value "Python 3.11, pytest"
binarybyte eval run --git-range HEAD~1..HEAD --version demo-1
binarybyte deploy run --version demo-1
```

---

## Install

```bash
pip install binarybyte
binarybyte --version
```

Optional extras:

- `pip install "binarybyte[sandbox]"` (Docker-based sandbox eval)
- `pip install "binarybyte[all]"`

From source (development):

```bash
git clone https://github.com/Aryannovice/BinaryByte.git
cd BinaryByte
pip install -e ".[dev]"
pytest
ruff check .
```

> Sandbox evaluation uses the Docker CLI when enabled in config.

---

## CLI commands (quick reference)

Global help:

```bash
binarybyte --help
binarybyte state --help
binarybyte eval --help
binarybyte deploy --help
```

Setup:

- Create `.binarybyte/`: `binarybyte init` (or `binarybyte init path/to/project`)

State:

- Add memory: `binarybyte state add --key K --value "V" [--source manual]`
- List entries: `binarybyte state list`
- List snapshots: `binarybyte state snapshots`
- Compare snapshots: `binarybyte state diff --from v1 --to v2`
- Restore state from snapshot: `binarybyte state rollback --version v1`

Eval:

- Evaluate a patch file: `binarybyte eval run --diff changes.patch [--version v1]`
- Evaluate a git range: `binarybyte eval run --git-range HEAD~1..HEAD [--version v1]`

Deploy:

- Deploy current state (defaults to latest verdict): `binarybyte deploy run [--version latest|v1]`
- Deploy from a previous snapshot: `binarybyte deploy rollback --version v1`
- Show deploy history: `binarybyte deploy history`

---

## Use in CI

BinaryByte is CI-friendly: `binarybyte eval run` exits non-zero when the verdict fails, so it can gate merges/releases.

Example:

```bash
binarybyte init .
binarybyte eval run --git-range "$BASE_SHA...$HEAD_SHA" --version "pr-123"
```

---

## What gets written on disk

After `init`, BinaryByte writes per project:

```
.binarybyte/
  config.yaml
  state.yaml
  results/<version>/verdict.json
  results/<version>/state_snapshot.yaml
  deploy_log.json
  plugins/*.py
  checks/*.py
```

---

## Deploy targets

Built-in deploy targets (when listed in `agents.targets` in `.binarybyte/config.yaml`):

| Target id | Output |
|-----------|--------|
| `cursor` | `.cursor/rules/binarybyte.mdc` |
| `gemini-cli` | `GEMINI.md` |
| `claude-code` | `CLAUDE.md` |
| `windsurf` | `.windsurfrules` |
| `copilot` | `.github/copilot-instructions.md` |

See the config template in `examples/sample-config.yaml`.

---

## Built-in evaluation (summary)

- **Safety** — denied command patterns + denied paths + optional secret scanning.
- **Imports** — flags new third-party imports that don’t resolve.
- **Secrets** — scans added lines for API-key-like patterns (configurable).
- **Plugins** — add custom checks under `.binarybyte/checks/`.
- **Sandbox (optional)** — run commands in a Docker container against a temp project copy with the patch applied.

---

## Plugins

Deploy adapters:

- Drop Python files into `.binarybyte/plugins/` that subclass `BaseAdapter`.
- See `examples/plugin_example.py`.

Eval checks:

- Add Python files under `.binarybyte/checks/` exposing `check(diff_text, config) -> CheckResult`.

---

## Releasing (maintainers)

1. Bump the version in `pyproject.toml`.
2. Tag and push `vX.Y.Z`.
3. GitHub Actions builds, validates (`twine check`), and publishes to PyPI via OIDC (Trusted Publishing).

---

## Contributing

Contributions are welcome—new adapters, new checks, docs, and examples.

- Run `pytest -q` and `ruff check .` before opening a PR.
- Keep PRs focused and add tests where practical.

See `CONTRIBUTING.md` for the full dev workflow.

---

## License

MIT — see [LICENSE](LICENSE).
