from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from binarybyte.core.config import BinaryByteConfig, load_config
from binarybyte.core.constants import get_results_dir
from binarybyte.eval.checks.imports import check_imports
from binarybyte.eval.checks.safety import check_denied_commands, check_denied_paths
from binarybyte.eval.schema import CheckResult, Verdict


class EvalRunner:
    def __init__(self, config: BinaryByteConfig | None = None, project_root: Path | None = None):
        self.project_root = project_root
        self.config = config or load_config(project_root)

    def run(self, diff_text: str, version: str = "latest") -> Verdict:
        results: list[CheckResult] = [
            check_denied_commands(diff_text, self.config),
            check_denied_paths(diff_text, self.config),
            check_imports(diff_text),
        ]

        verdict = Verdict(
            version=version,
            passed=all(r.passed for r in results),
            checks=results,
            timestamp=datetime.now(timezone.utc),
        )

        self._save_verdict(verdict)
        return verdict

    def _save_verdict(self, verdict: Verdict) -> Path:
        results_dir = get_results_dir(self.project_root) / verdict.version
        results_dir.mkdir(parents=True, exist_ok=True)
        path = results_dir / "verdict.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(verdict.model_dump(mode="json"), f, indent=2, default=str)
        return path
