# BinaryByte

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**One CLI to evaluate agent-proposed changes, keep shared agent state, and deploy verified rules to Cursor, Gemini CLI, Claude Code, Windsurf, Copilot, and custom targets.**

**Current version:** 0.3.0

---

## Why BinaryByte

If you switch between editors and agents, context drifts. It is also easy to merge risky diffs. BinaryByte gives you:

1. **Eval** — Run checks on a patch or `git diff` range; store a **verdict** and a **state snapshot** per version label.
2. **State** — One canonical `state.yaml` (memory + conventions) that all targets can receive.
3. **Deploy** — Push that state into each tool’s native file format, **only** if the verdict for the version you choose **passed** (the deploy gate).

---

## Install

```bash
pip install binarybyte
binarybyte --version
```

**From source (development):**

```bash
git clone https://github.com/BinaryByte-project/BinaryByte.git
cd BinaryByte
pip install -e ".[dev]"
```

**Optional:** `pip install "binarybyte[sandbox]"` or `"binarybyte[all]"` (extra PyPI deps). **Sandbox** evaluation still relies on the **Docker CLI** (`docker info` / `docker run`) when `eval.sandbox.enabled` is `true` in config.

---

## CLI commands (quick reference)

Run these from your **project root** (where you ran `init`). Global help:

```bash
binarybyte --help
binarybyte state --help
binarybyte eval --help
binarybyte deploy --help
```

| Action | Command |
|--------|---------|
| Show version | `binarybyte --version` |
| Guided menu | `binarybyte interactive` |

**Setup**

| Action | Command |
|--------|---------|
| Create `.binarybyte/` | `binarybyte init` or `binarybyte init path/to/project` |

**State (canonical notebook)**

| Action | Command |
|--------|---------|
| Add memory | `binarybyte state add --key K --value "V" [--source manual]` |
| List entries | `binarybyte state list` |
| List snapshot versions | `binarybyte state snapshots` |
| Compare two snapshots | `binarybyte state diff --from v1 --to v2` |
| Restore `state.yaml` from snapshot | `binarybyte state rollback --version v1` |

**Eval**

| Action | Command |
|--------|---------|
| Evaluate a patch file | `binarybyte eval run --diff changes.patch [--version v1]` |
| Evaluate a git range | `binarybyte eval run --git-range HEAD~1..HEAD [--version v1]` |

Each successful run writes under `.binarybyte/results/<version>/`:

- `verdict.json` — pass/fail and per-check details  
- `state_snapshot.yaml` — copy of state at eval time  

**Deploy**

| Action | Command |
|--------|---------|
| Deploy current state to all targets | `binarybyte deploy run [--version latest\|v1]` |
| Deploy + gate using a snapshot | `binarybyte deploy rollback --version v1` |
| Show deploy log | `binarybyte deploy history` |

`deploy run` without `--version` defaults to **`latest`**: the most recently modified verdict folder under `results/`. Deploy is **blocked** if that verdict’s overall result is not a pass.

---

## Typical workflow (copy-paste)

```bash
binarybyte init
binarybyte state add --key "stack" --value "Python 3.11, FastAPI, pytest"
binarybyte eval run --diff my-change.patch --version release-1
binarybyte deploy run --version release-1
```

After more edits and evals:

```bash
binarybyte state snapshots
binarybyte state diff --from release-1 --to release-2
binarybyte deploy history
```

---

## What gets written on disk

**Per project** (after `init`):

```
.binarybyte/
  config.yaml          # targets, safety rules, optional sandbox
  state.yaml           # memory + conventions
  results/<version>/verdict.json
  results/<version>/state_snapshot.yaml
  deploy_log.json      # after deploy run / rollback
  plugins/*.py         # optional: custom deploy adapters
  checks/*.py          # optional: custom eval checks (CheckResult)
```

**Built-in deploy targets** (when listed in `agents.targets` in `config.yaml`):

| Target id | Output |
|-----------|--------|
| `cursor` | `.cursor/rules/binarybyte.mdc` |
| `gemini-cli` | `GEMINI.md` |
| `claude-code` | `CLAUDE.md` |
| `windsurf` | `.windsurfrules` |
| `copilot` | `.github/copilot-instructions.md` |

Defaults usually include `cursor` and `gemini-cli`; add others in `config.yaml`. See **`examples/sample-config.yaml`** for a full template.

---

## Built-in evaluation (summary)

- **Safety** — Patterns for denied shell / SQL-like strings; paths you must not modify in the diff.
- **Imports** — Flags added third-party imports that are not resolvable (helps catch “hallucinated” deps).
- **Secrets** — Regex-style scan on added lines (API key–like patterns); configurable or disable via `eval.safety`.
- **Plugins** — Python files in `.binarybyte/checks/` exposing `check(diff_text, config) -> CheckResult`.
- **Sandbox** (optional) — If enabled and Docker is available, runs configured commands inside `docker run` against a temp copy of the project with the patch applied.

---

## How the pieces fit together

```
  You
   |
   |  binarybyte init / state / eval / deploy
   v
 .binarybyte/  --------->  verdict + snapshot per version
   |
   +--> deploy gate --> adapters --> Cursor / Gemini / etc. files
```

---

## Plugins

- **Deploy:** subclass `BaseAdapter`, put `.py` files in `.binarybyte/plugins/`. See `examples/plugin_example.py`.
- **Eval:** implement `check(diff_text, config)` returning `CheckResult` in `.binarybyte/checks/`.

---

## Development (this repository)

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

---

## Roadmap and what is next

**Shipped in 0.3.x:** eval (safety, imports, secrets, plugins, optional Docker sandbox), state snapshots / diff / rollback, deploy gate, multiple built-in adapters, deploy history and deploy rollback, PyPI-oriented packaging.

**Planned for future releases (e.g. 0.4+):** tighter CI / recipe templates, optional remote or team-shared state, watch-mode or hook-friendly workflows, and more adapters as agent tools evolve. APIs and file layouts may gain small extensions; we will keep **defaults backward-friendly** where possible and document breaking changes in release notes.

---

## Contributing

1. Fork the repo and branch from `main` (`feat/...`, `fix/...`, `docs/...`).
2. Run `pytest` and `ruff check .` before opening a PR.
3. One focused change per pull request when practical.

---

## Contact

Questions, collaborations, or feedback:

- **Ayush Pandey** — [ayushpandey1177@gmail.com](mailto:ayushpandey1177@gmail.com)
- **Aloukik Joshi** — [aloukikjoshi@gmail.com](mailto:aloukikjoshi@gmail.com)

Either address is fine; we’ll route or reply as appropriate.

---

## License

[MIT](LICENSE)
