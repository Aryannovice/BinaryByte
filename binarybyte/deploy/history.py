from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from binarybyte.core.constants import get_bb_dir

DEPLOY_LOG_FILE = "deploy_log.json"


def _log_path(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / DEPLOY_LOG_FILE


def _compute_state_hash(state_yaml_path: Path) -> str:
    if not state_yaml_path.exists():
        return "unknown"
    content = state_yaml_path.read_bytes()
    return f"sha256:{hashlib.sha256(content).hexdigest()[:16]}"


def append_deploy_log(
    version: str,
    target_results: list[tuple[str, bool, str]],
    project_root: Path | None = None,
    rollback: bool = False,
) -> None:
    path = _log_path(project_root)
    log: list[dict] = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            log = json.load(f)

    from binarybyte.core.constants import get_state_path

    state_hash = _compute_state_hash(get_state_path(project_root))

    entry = {
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "targets": {name: "OK" if ok else f"FAIL: {msg}" for name, ok, msg in target_results},
        "state_hash": state_hash,
        "rollback": rollback,
    }
    log.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


def read_deploy_log(project_root: Path | None = None) -> list[dict]:
    path = _log_path(project_root)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)
