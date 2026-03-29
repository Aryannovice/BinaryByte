import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.deploy.history import append_deploy_log, read_deploy_log
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="history-test"), root)
    return root


def test_read_empty_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        assert read_deploy_log(root) == []


def test_append_and_read_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        results = [("cursor", True, "/path/to/rules"), ("gemini-cli", True, "/path/to/gemini")]
        append_deploy_log("v1", results, project_root=root)

        log = read_deploy_log(root)
        assert len(log) == 1
        assert log[0]["version"] == "v1"
        assert log[0]["targets"]["cursor"] == "OK"
        assert log[0]["targets"]["gemini-cli"] == "OK"
        assert log[0]["rollback"] is False


def test_append_multiple_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        append_deploy_log("v1", [("cursor", True, "ok")], project_root=root)
        append_deploy_log("v2", [("cursor", True, "ok")], project_root=root)
        append_deploy_log("v2", [("cursor", True, "ok")], project_root=root, rollback=True)

        log = read_deploy_log(root)
        assert len(log) == 3
        assert log[2]["rollback"] is True


def test_failed_target_logged():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        results = [("cursor", True, "ok"), ("bad-target", False, "adapter not found")]
        append_deploy_log("v1", results, project_root=root)

        log = read_deploy_log(root)
        assert "FAIL" in log[0]["targets"]["bad-target"]


def test_log_has_state_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        append_deploy_log("v1", [("cursor", True, "ok")], project_root=root)
        log = read_deploy_log(root)
        assert log[0]["state_hash"].startswith("sha256:")
