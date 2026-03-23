# BinaryByte

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**Infrastructure layer for AI coding agents — evaluate, sync, and deploy agent configs across tools.**

You use multiple AI coding agents (Cursor, Gemini CLI, Claude Code, etc.) across your workflow. They don't share context. You can't verify they're safe. You deploy configs manually. BinaryByte fixes that with a single CLI.

---

## How It Works

BinaryByte sits between you and your AI agents, providing three layers:

```
Developer
    |
    v
+---------------------------+
|        BinaryByte         |
|  eval  |  sync  | deploy  |
+----+--------+--------+---+
     |        |        |
     v        v        v
  Gemini   Cursor   (more
   CLI     Agent    agents)
```

**Evaluation Layer** — Every agent update is tested against safety rules. Automated checks catch unsafe behavior (deleting files, hallucinated imports, denied commands). Only passing changes move forward.

**State & Data Sync** — Agent memory and context are stored in a canonical format. If an agent learns something in the terminal, that knowledge is available when you open your editor.

**Deployment Gate** — Verified agent configs are deployed simultaneously across all supported environments. One source of truth, fanned out to each agent's native format.

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for sandboxed evaluation)

### Install

```bash
pip install binarybyte
```

Or install from source for development:

```bash
git clone https://github.com/BinaryByte-project/BinaryByte.git
cd BinaryByte
pip install -e ".[dev]"
```

### First Run

```bash
# 1. Initialize BinaryByte in your project
binarybyte init

# 2. Add shared context that all agents can access
binarybyte state add --key "api-pattern" --value "REST endpoints in src/api/, using FastAPI"

# 3. List what agents know
binarybyte state list

# 4. Evaluate a set of changes for safety
binarybyte eval run --diff changes.patch

# 5. Deploy verified config to all target agents
binarybyte deploy run
```

---

## Walkthrough: Full End-to-End Example

Follow these steps to see every feature in action.

### Step 1 — Initialize a project

```bash
mkdir my-project && cd my-project
binarybyte init .
```

This creates `.binarybyte/` with a default `config.yaml` (safety rules, target agents) and an empty `state.yaml`.

### Step 2 — Add shared knowledge

```bash
binarybyte state add --key "framework" --value "FastAPI for REST endpoints"
binarybyte state add --key "testing" --value "Always use pytest" --source "gemini-cli"
binarybyte state list
```

You'll see a table of memory entries. These are what every target agent will receive on deploy.

### Step 3 — Evaluate a safe change

Create a file called `good.patch`:

```diff
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,4 @@
+import os
+import json
 def main():
-    pass
+    print("hello")
```

Run the eval:

```bash
binarybyte eval run --diff good.patch --version v1
```

All three checks (denied commands, denied paths, hallucinated imports) should show **PASS**. A verdict file is written to `.binarybyte/results/v1/verdict.json`.

### Step 4 — Evaluate an unsafe change

Create a file called `bad.patch`:

```diff
diff --git a/.env b/.env
--- a/.env
+++ b/.env
@@ -1 +1,2 @@
 DB=localhost
+SECRET=leaked
diff --git a/nuke.sh b/nuke.sh
--- a/nuke.sh
+++ b/nuke.sh
@@ -1 +1,2 @@
 #!/bin/bash
+rm -rf /
```

Run the eval:

```bash
binarybyte eval run --diff bad.patch --version v2
```

This time you'll see **FAIL** for denied commands (`rm -rf /`) and denied paths (`.env` modified). The verdict blocks deployment.

### Step 5 — Deploy to agents

Deploy the passing version:

```bash
binarybyte deploy run --version v1
```

This writes:
- `.cursor/rules/binarybyte.mdc` — Cursor picks this up automatically as project rules
- `GEMINI.md` — Gemini CLI reads this as project context

Try deploying the failing version:

```bash
binarybyte deploy run --version v2
```

The gate blocks it with "Deploy blocked. Version 'v2' failed evaluation."

### Step 6 — Run the test suite

Back in the BinaryByte repo root:

```bash
pytest tests/ -v
```

All 30 tests should pass, covering config loading, state management, eval checks, and deploy adapters.

---

## Architecture

```
BinaryByte/
  binarybyte/
    cli/                     # Typer CLI commands
      main.py                #   App entrypoint and subcommand wiring
      init_cmd.py            #   binarybyte init
      state_cmd.py           #   binarybyte state add / list
      eval_cmd.py            #   binarybyte eval run
      deploy_cmd.py          #   binarybyte deploy run
    core/                    # Shared utilities
      config.py              #   Load/validate .binarybyte/config.yaml
      constants.py           #   Paths, directory names, defaults
    eval/                    # Evaluation engine
      runner.py              #   Orchestrate checks, produce verdict
      checks/
        safety.py            #   Denied commands and paths scanner
        imports.py           #   Hallucinated import detector
    state/                   # State management
      schema.py              #   Pydantic models for agent state
      store.py               #   Read/write .binarybyte/state.yaml
    deploy/                  # Deployment engine
      gate.py                #   Verify eval passed before deploy
      manifest.py            #   Agent manifest parsing
      targets/
        base.py              #   Abstract adapter interface
        cursor.py            #   Cursor rules adapter
        gemini_cli.py        #   Gemini CLI context adapter
  tests/                     # pytest test suite
  examples/                  # Sample config and state files
```

### The `.binarybyte/` Directory

When you run `binarybyte init`, a `.binarybyte/` directory is created in your project root:

```
.binarybyte/
  config.yaml    # Project configuration (targets, safety rules)
  state.yaml     # Canonical agent state (memory, conventions)
  results/       # Evaluation verdicts (auto-generated)
```

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Canonical State** | The single source of truth for agent context — conventions, memory entries, and tool config stored in `.binarybyte/state.yaml`. |
| **Eval Suite** | A set of automated checks (safety, imports, etc.) that validate agent-proposed changes before they're accepted. |
| **Adapter** | A plugin that translates canonical state into a specific agent's native config format (e.g., Cursor rules, Gemini context). |
| **Deploy Target** | An AI agent environment that BinaryByte can push configs to (e.g., `cursor`, `gemini-cli`). |
| **Verdict** | The pass/fail result of an eval run, stored in `.binarybyte/results/`. |
| **Gate** | The deploy gate — blocks deployment unless the latest eval verdict is a pass. |

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `binarybyte init [DIR]` | Initialize BinaryByte in a project directory |
| `binarybyte state add --key K --value V` | Add a memory entry to the shared state |
| `binarybyte state list` | List all memory entries |
| `binarybyte eval run --diff FILE` | Run safety and correctness checks against a diff |
| `binarybyte deploy run` | Deploy verified config to all target agents |
| `binarybyte --version` | Show version |
| `binarybyte --help` | Show help |

---

## Supported Agents

| Agent | Status | Adapter |
|-------|--------|---------|
| **Cursor** | Supported | Writes `.cursor/rules/binarybyte.mdc` |
| **Gemini CLI** | Supported | Writes `GEMINI.md` project context |
| Claude Code | Planned | — |
| Aider | Planned | — |

### Adding Your Own Adapter

Create a new file in `binarybyte/deploy/targets/` that implements `BaseAdapter`:

```python
from binarybyte.deploy.targets.base import BaseAdapter

class MyAgentAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my-agent"

    def deploy(self, state, config) -> None:
        # Write your agent's config format here
        ...
```

Then register it in `binarybyte/deploy/targets/__init__.py`.

---

## Development Setup

```bash
# Clone the repo
git clone https://github.com/BinaryByte-project/BinaryByte.git
cd BinaryByte

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run the CLI
binarybyte --help

# Run tests
pytest

# Lint
ruff check binarybyte/
```

### Branch Naming

- `feat/<short-description>` for new features
- `fix/<short-description>` for bug fixes
- `docs/<short-description>` for documentation

### Pull Requests

- One feature per PR
- Include a description of what changed and why
- Make sure `pytest` passes before opening

---

## Roadmap

- [x] Project scaffold and CLI skeleton
- [x] `binarybyte init` + config/state schemas
- [x] `binarybyte state add/list`
- [x] Eval runner with safety checks (denied commands, denied paths, hallucinated imports)
- [x] Deploy gate + Cursor adapter
- [x] Deploy gate + Gemini CLI adapter
- [x] Test suite (30 tests)
- [ ] Docker-based sandboxed evaluation
- [ ] CI/CD pipeline integration
- [ ] Remote state sync (cloud backend)
- [ ] Additional agent adapters (Claude Code, Aider, etc.)

---

## Contributing

Contributions are welcome! This project is in early development, so there's plenty to do.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run `pytest` and `ruff check binarybyte/`
5. Open a PR against `main`

If you're unsure where to start, check the roadmap above or open an issue to discuss.

---

## License

[MIT](LICENSE)
