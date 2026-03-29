import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from binarybyte.core.config import SandboxConfig, default_config, save_config
from binarybyte.eval.sandbox.runner import run_sandbox
from binarybyte.eval.runner import EvalRunner
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state

SAFE_DIFF = """\
diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1 +1,2 @@
+print("hello")
"""


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="sandbox-test"), root)
    return root


def test_sandbox_disabled_returns_empty():
    config = SandboxConfig(enabled=False)
    results = run_sandbox(SAFE_DIFF, config)
    assert results == []


def test_sandbox_default_config_disabled():
    config = default_config()
    assert config.eval.sandbox.enabled is False


@patch("binarybyte.eval.sandbox.runner._docker_available", return_value=False)
def test_sandbox_no_docker_skips(mock_docker):
    config = SandboxConfig(enabled=True, commands=["pytest -q"])
    results = run_sandbox(SAFE_DIFF, config)
    assert len(results) == 1
    assert results[0].passed is True
    assert "skipped" in results[0].details[0].lower()


@patch("binarybyte.eval.sandbox.runner._docker_available", return_value=True)
@patch("binarybyte.eval.sandbox.runner.subprocess.run")
def test_sandbox_command_passes(mock_run, mock_docker):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=b"1 passed in 0.1s",
        stderr=b"",
    )
    config = SandboxConfig(enabled=True, commands=["pytest -q"])

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("pass\n")
        results = run_sandbox(SAFE_DIFF, config, project_root=root)

    assert len(results) == 1
    assert results[0].passed is True
    assert "passed" in results[0].details[0].lower()


@patch("binarybyte.eval.sandbox.runner._docker_available", return_value=True)
@patch("binarybyte.eval.sandbox.runner.subprocess.run")
def test_sandbox_command_fails(mock_run, mock_docker):
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout=b"",
        stderr=b"FAILED test_foo.py",
    )
    config = SandboxConfig(enabled=True, commands=["pytest -q"])

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("pass\n")
        results = run_sandbox(SAFE_DIFF, config, project_root=root)

    assert len(results) == 1
    assert results[0].passed is False


@patch("binarybyte.eval.sandbox.runner._docker_available", return_value=True)
@patch("binarybyte.eval.sandbox.runner.subprocess.run")
def test_sandbox_timeout(mock_run, mock_docker):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="docker", timeout=120)
    config = SandboxConfig(enabled=True, commands=["pytest -q"], timeout_seconds=120)

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("pass\n")
        results = run_sandbox(SAFE_DIFF, config, project_root=root)

    assert len(results) == 1
    assert results[0].passed is False
    assert "timed out" in results[0].details[0].lower()


@patch("binarybyte.eval.sandbox.runner._docker_available", return_value=True)
@patch("binarybyte.eval.sandbox.runner.subprocess.run")
def test_sandbox_multiple_commands(mock_run, mock_docker):
    mock_run.return_value = MagicMock(returncode=0, stdout=b"ok", stderr=b"")
    config = SandboxConfig(enabled=True, commands=["pytest -q", "ruff check ."])

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("pass\n")
        results = run_sandbox(SAFE_DIFF, config, project_root=root)

    assert len(results) == 2
    assert all(r.passed for r in results)


def test_eval_runner_skips_sandbox_when_disabled():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        runner = EvalRunner(project_root=root)
        verdict = runner.run(SAFE_DIFF, version="v1")
        sandbox_checks = [c for c in verdict.checks if c.name.startswith("sandbox")]
        assert len(sandbox_checks) == 0


def test_sandbox_config_defaults():
    config = SandboxConfig()
    assert config.enabled is False
    assert config.image == "python:3.11-slim"
    assert config.timeout_seconds == 120
    assert config.commands == ["pytest -q"]
