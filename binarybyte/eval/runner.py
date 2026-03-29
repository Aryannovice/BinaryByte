from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from binarybyte.core.config import BinaryByteConfig, load_config
from binarybyte.core.constants import get_results_dir
from binarybyte.eval.checks.imports import check_imports
from binarybyte.eval.checks.loader import load_eval_plugins
from binarybyte.eval.checks.safety import check_denied_commands, check_denied_paths
from binarybyte.eval.checks.secrets import check_secrets
from binarybyte.eval.sandbox.runner import run_sandbox
from binarybyte.eval.schema import CheckResult, Verdict
from binarybyte.state.snapshots import snapshot_state


class EvalRunner:
    def __init__(self, config: BinaryByteConfig | None = None, project_root: Path | None = None):
        self.project_root = project_root
        self.config = config or load_config(project_root)

    def run(self, diff_text: str, version: str = "latest") -> Verdict:
        results: list[CheckResult] = [
            check_denied_commands(diff_text, self.config),
            check_denied_paths(diff_text, self.config),
            check_imports(diff_text),
            check_secrets(diff_text, self.config),
        ]

        plugin_results = load_eval_plugins(diff_text, self.config, self.project_root)
        results.extend(plugin_results)

        sandbox_results = run_sandbox(diff_text, self.config.eval.sandbox, self.project_root)
        results.extend(sandbox_results)

        verdict = Verdict(
            version=version,
            passed=all(r.passed for r in results),
            checks=results,
            timestamp=datetime.now(timezone.utc),
        )

        self._save_verdict(verdict)
        self._snapshot_state(version)
        return verdict

    def _snapshot_state(self, version: str) -> None:
        try:
            snapshot_state(version, self.project_root)
        except FileNotFoundError:
            pass

    def _save_verdict(self, verdict: Verdict) -> Path:
        results_dir = get_results_dir(self.project_root) / verdict.version
        results_dir.mkdir(parents=True, exist_ok=True)
        path = results_dir / "verdict.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(verdict.model_dump(mode="json"), f, indent=2, default=str)
        return path
