import json
import tempfile
from pathlib import Path
import os

from binarybyte.core.config import default_config, save_config
from binarybyte.eval.results import find_latest_passed_version
from binarybyte.eval.schema import Verdict, CheckResult
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="last-passed-test"), root)
    return root


def _write_verdict(root: Path, version: str, passed: bool, mtime: float | None = None) -> None:
    verdict = Verdict(
        version=version,
        passed=passed,
        checks=[CheckResult(name="test", passed=passed, details=["detail"])],
    )
    out_dir = root / ".binarybyte" / "results" / version
    out_dir.mkdir(parents=True, exist_ok=True)
    verdict_path = out_dir / "verdict.json"
    verdict_path.write_text(
        json.dumps(verdict.model_dump(mode="json"), default=str),
        encoding="utf-8",
    )
    if mtime is not None:
        os.utime(verdict_path, (mtime, mtime))


def test_find_latest_passed_version_none_when_no_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        assert find_latest_passed_version(root) is None


def test_find_latest_passed_version_picks_most_recent_passing():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_verdict(root, "v1", passed=False, mtime=1)
        _write_verdict(root, "v2", passed=True, mtime=2)
        _write_verdict(root, "v3", passed=True, mtime=3)
        assert find_latest_passed_version(root) == "v3"
