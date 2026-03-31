from __future__ import annotations

import json
from pathlib import Path

from binarybyte.core.constants import get_results_dir
from binarybyte.eval.schema import Verdict


def find_latest_passed_version(project_root: Path | None = None) -> str | None:
    """Return the most recent version whose verdict passed.

    Uses verdict.json modification time as the ordering signal.
    """

    results_dir = get_results_dir(project_root)
    if not results_dir.exists():
        return None

    candidates: list[Path] = []
    for d in results_dir.iterdir():
        if not d.is_dir():
            continue
        verdict_path = d / "verdict.json"
        if not verdict_path.exists():
            continue
        try:
            raw = json.loads(verdict_path.read_text(encoding="utf-8"))
            verdict = Verdict.model_validate(raw)
        except Exception:
            continue
        if verdict.passed:
            candidates.append(verdict_path)

    if not candidates:
        return None

    latest = max(
        candidates,
        key=lambda p: (p.stat().st_mtime, p.parent.name),
    )
    return latest.parent.name
