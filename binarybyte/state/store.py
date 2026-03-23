from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from binarybyte.core.constants import get_state_path
from binarybyte.state.schema import AgentState, MemoryEntry


def read_state(project_root: Path | None = None) -> AgentState:
    path = get_state_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"State file not found at {path}. Run 'binarybyte init' first."
        )
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AgentState.model_validate(raw)


def write_state(state: AgentState, project_root: Path | None = None) -> Path:
    path = get_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = state.model_dump()
    for entry in data.get("memory", []):
        if isinstance(entry.get("timestamp"), datetime):
            entry["timestamp"] = entry["timestamp"].isoformat()
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    return path


def add_memory(
    key: str,
    value: str,
    source: str = "manual",
    project_root: Path | None = None,
) -> MemoryEntry:
    state = read_state(project_root)
    entry = MemoryEntry(
        key=key,
        value=value,
        source=source,
        timestamp=datetime.now(timezone.utc),
    )
    state.memory.append(entry)
    write_state(state, project_root)
    return entry
