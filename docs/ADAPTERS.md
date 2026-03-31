# Writing deploy adapters (targets)

BinaryByte deploy targets are adapters that render the canonical agent state into a tool-specific file format.

This project supports **project-local adapters** via plugins:

- Put adapter files in `.binarybyte/plugins/*.py`
- Each adapter must subclass `BaseAdapter` and define `NAME`
- Add the adapter name to `agents.targets` in `.binarybyte/config.yaml`

## Minimal adapter template

Start from the example in `examples/plugin_example.py`.

A minimal adapter looks like:

```python
from pathlib import Path

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class MyToolAdapter(BaseAdapter):
    NAME = "my-tool"

    @property
    def name(self) -> str:
        return self.NAME

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        out_path = self.project_root / "MY_TOOL_RULES.md"
        out_path.write_text("# Rules\n", encoding="utf-8")
        return out_path
```

## Cookbook (tiny)

These examples are intentionally minimal and meant to be copied into `.binarybyte/plugins/`.

### 1) Markdown target (single file)

Writes `MY_TOOL.md` with project name + conventions + memory.

```python
from pathlib import Path

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class MyMarkdownToolAdapter(BaseAdapter):
    NAME = "my-markdown-tool"

    @property
    def name(self) -> str:
        return self.NAME

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        out_path = self.project_root / "MY_TOOL.md"
        lines: list[str] = ["# BinaryByte Rules", "", f"Project: {state.project_name}"]
        if state.conventions:
            lines += ["", "## Conventions"]
            lines += [f"- {c}" for c in state.conventions]
        if state.memory:
            lines += ["", "## Memory"]
            lines += [f"- {m.key}: {m.value}" for m in state.memory]
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return out_path
```

### 2) YAML target (structured)

Writes `.mytool/rules.yaml` containing conventions and memory as a mapping.

```python
from pathlib import Path

import yaml

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class MyYamlToolAdapter(BaseAdapter):
    NAME = "my-yaml-tool"

    @property
    def name(self) -> str:
        return self.NAME

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        out_dir = self.project_root / ".mytool"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "rules.yaml"
        payload = {
            "project": state.project_name,
            "conventions": state.conventions or [],
            "memory": {m.key: m.value for m in (state.memory or [])},
        }
        out_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return out_path
```

### 3) JSON target (structured)

Writes `.mytool/rules.json` with the same payload.

```python
from __future__ import annotations

from pathlib import Path
import json

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class MyJsonToolAdapter(BaseAdapter):
    NAME = "my-json-tool"

    @property
    def name(self) -> str:
        return self.NAME

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        out_dir = self.project_root / ".mytool"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "rules.json"
        payload = {
            "project": state.project_name,
            "conventions": state.conventions or [],
            "memory": [{"key": m.key, "value": m.value} for m in (state.memory or [])],
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return out_path
```

### Enabling your target

Add your adapter name under `agents.targets`:

```yaml
agents:
  targets:
    - my-markdown-tool
```

## What to include in an adapter PR

- The adapter implementation
- A short README snippet describing the tool’s expected file path and format
- A test that asserts the output path and basic content

## Request checklist

When requesting support for a new tool, include:

- Tool name + docs link
- Exact output file path(s)
- Expected format + minimal example
- Constraints (frontmatter, size limits, etc.)
