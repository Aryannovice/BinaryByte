from __future__ import annotations

import shutil
from pathlib import Path

from binarybyte.core.constants import get_results_dir, get_state_path
from binarybyte.state.schema import AgentState

import yaml

SNAPSHOT_FILE = "state_snapshot.yaml"


def snapshot_state(version: str, project_root: Path | None = None) -> Path:
    """Copy current state.yaml into results/<version>/state_snapshot.yaml."""
    state_path = get_state_path(project_root)
    if not state_path.exists():
        raise FileNotFoundError(
            f"State file not found at {state_path}. Run 'binarybyte init' first."
        )

    dest_dir = get_results_dir(project_root) / version
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / SNAPSHOT_FILE
    shutil.copy2(state_path, dest)
    return dest


def load_snapshot(version: str, project_root: Path | None = None) -> AgentState:
    """Load a historical state snapshot."""
    snap_path = get_results_dir(project_root) / version / SNAPSHOT_FILE
    if not snap_path.exists():
        raise FileNotFoundError(
            f"No state snapshot found for version '{version}'. "
            f"Snapshots are created automatically during eval."
        )
    with open(snap_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AgentState.model_validate(raw)


def list_snapshots(project_root: Path | None = None) -> list[str]:
    """List all versions that have state snapshots."""
    results_dir = get_results_dir(project_root)
    if not results_dir.exists():
        return []
    return sorted(
        d.name
        for d in results_dir.iterdir()
        if d.is_dir() and (d / SNAPSHOT_FILE).exists()
    )
