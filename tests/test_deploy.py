import json
import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.deploy.gate import check_gate, find_latest_version
from binarybyte.deploy.manifest import get_adapter, list_available_targets
from binarybyte.deploy.targets.cursor import CursorAdapter
from binarybyte.deploy.targets.gemini_cli import GeminiCliAdapter
from binarybyte.eval.schema import Verdict, CheckResult
from binarybyte.state.schema import AgentState
from binarybyte.state.store import add_memory, write_state


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    state = AgentState(project_name="deploy-test")
    write_state(state, root)
    add_memory("framework", "FastAPI", project_root=root)
    return root


def _write_verdict(root: Path, version: str, passed: bool) -> None:
    verdict = Verdict(
        version=version,
        passed=passed,
        checks=[CheckResult(name="test", passed=passed, details=["test detail"])],
    )
    results_dir = root / ".binarybyte" / "results" / version
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "verdict.json", "w") as f:
        json.dump(verdict.model_dump(mode="json"), f, default=str)


def test_check_gate_passes():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_verdict(root, "v1", passed=True)
        verdict = check_gate("v1", root)
        assert verdict.passed is True


def test_check_gate_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_verdict(root, "v1", passed=False)
        verdict = check_gate("v1", root)
        assert verdict.passed is False


def test_check_gate_missing_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        try:
            check_gate("nonexistent", root)
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_find_latest_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_verdict(root, "v1", passed=True)
        _write_verdict(root, "v2", passed=True)
        latest = find_latest_version(root)
        assert latest in ("v1", "v2")


def test_find_latest_version_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        assert find_latest_version(root) is None


def test_list_available_targets():
    targets = list_available_targets()
    assert "cursor" in targets
    assert "gemini-cli" in targets


def test_get_adapter_cursor():
    adapter = get_adapter("cursor")
    assert isinstance(adapter, CursorAdapter)


def test_get_adapter_gemini():
    adapter = get_adapter("gemini-cli")
    assert isinstance(adapter, GeminiCliAdapter)


def test_get_adapter_unknown():
    try:
        get_adapter("nonexistent-agent")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_cursor_adapter_deploy():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        state = AgentState(project_name="test")
        state.memory.append(
            __import__("binarybyte.state.schema", fromlist=["MemoryEntry"]).MemoryEntry(
                key="lang", value="Python"
            )
        )
        config = default_config()
        adapter = CursorAdapter(project_root=root)
        path = adapter.deploy(state, config)
        assert path.exists()
        content = path.read_text()
        assert "lang" in content
        assert "Python" in content


def test_gemini_adapter_deploy():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        state = AgentState(project_name="test")
        config = default_config()
        adapter = GeminiCliAdapter(project_root=root)
        path = adapter.deploy(state, config)
        assert path.exists()
        assert "BinaryByte Context" in path.read_text()
