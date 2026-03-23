from __future__ import annotations

import json
from pathlib import Path

from binarybyte.core.constants import get_results_dir
from binarybyte.eval.schema import Verdict


def check_gate(version: str, project_root: Path | None = None) -> Verdict:
    """Load the verdict for a given version and return it.

    Raises FileNotFoundError if no verdict exists for the version.
    """
    verdict_path = get_results_dir(project_root) / version / "verdict.json"
    if not verdict_path.exists():
        raise FileNotFoundError(
            f"No eval verdict found for version '{version}'. "
            f"Run 'binarybyte eval run --diff <file> --version {version}' first."
        )
    with open(verdict_path, encoding="utf-8") as f:
        raw = json.load(f)
    return Verdict.model_validate(raw)


def find_latest_version(project_root: Path | None = None) -> str | None:
    """Find the most recently evaluated version by file modification time."""
    results_dir = get_results_dir(project_root)
    if not results_dir.exists():
        return None
    versions = [
        d for d in results_dir.iterdir()
        if d.is_dir() and (d / "verdict.json").exists()
    ]
    if not versions:
        return None
    latest = max(versions, key=lambda d: (d / "verdict.json").stat().st_mtime)
    return latest.name
