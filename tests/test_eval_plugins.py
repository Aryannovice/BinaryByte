import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.eval.checks.loader import load_eval_plugins
from binarybyte.eval.runner import EvalRunner
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state

PASSING_PLUGIN = """\
from binarybyte.eval.schema import CheckResult

def check(diff_text, config):
    return CheckResult(name="custom_pass", passed=True, details=["All good."])
"""

FAILING_PLUGIN = """\
from binarybyte.eval.schema import CheckResult

def check(diff_text, config):
    if "dangerous" in diff_text:
        return CheckResult(name="custom_fail", passed=False, details=["Found dangerous code."])
    return CheckResult(name="custom_fail", passed=True, details=["Clean."])
"""

BAD_PLUGIN_NO_FUNC = """\
x = 42
"""

BAD_PLUGIN_WRONG_RETURN = """\
def check(diff_text, config):
    return "not a CheckResult"
"""

SAFE_DIFF = """\
diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1 +1,2 @@
+print("hello")
"""

DANGEROUS_DIFF = """\
diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1 +1,2 @@
+dangerous()
"""


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="plugin-test"), root)
    return root


def _write_plugin(root: Path, filename: str, content: str) -> None:
    checks_dir = root / ".binarybyte" / "checks"
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / filename).write_text(content, encoding="utf-8")


def test_no_plugins_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        results = load_eval_plugins(SAFE_DIFF, default_config(), root)
        assert results == []


def test_passing_plugin():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "good_check.py", PASSING_PLUGIN)
        results = load_eval_plugins(SAFE_DIFF, default_config(), root)
        assert len(results) == 1
        assert results[0].passed is True
        assert "plugin:" in results[0].name


def test_failing_plugin():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "danger_check.py", FAILING_PLUGIN)
        results = load_eval_plugins(DANGEROUS_DIFF, default_config(), root)
        assert len(results) == 1
        assert results[0].passed is False


def test_plugin_no_check_function():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "bad_check.py", BAD_PLUGIN_NO_FUNC)
        results = load_eval_plugins(SAFE_DIFF, default_config(), root)
        assert len(results) == 1
        assert results[0].passed is False
        assert "no callable" in results[0].details[0].lower()


def test_plugin_wrong_return_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "wrong_return.py", BAD_PLUGIN_WRONG_RETURN)
        results = load_eval_plugins(SAFE_DIFF, default_config(), root)
        assert len(results) == 1
        assert results[0].passed is False


def test_multiple_plugins():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "check_a.py", PASSING_PLUGIN)
        _write_plugin(root, "check_b.py", PASSING_PLUGIN)
        results = load_eval_plugins(SAFE_DIFF, default_config(), root)
        assert len(results) == 2
        assert all(r.passed for r in results)


def test_eval_runner_includes_plugins():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        _write_plugin(root, "custom.py", FAILING_PLUGIN)
        runner = EvalRunner(project_root=root)
        verdict = runner.run(DANGEROUS_DIFF, version="v1")
        assert verdict.passed is False
        plugin_checks = [c for c in verdict.checks if c.name.startswith("plugin:")]
        assert len(plugin_checks) == 1
        assert plugin_checks[0].passed is False


def test_eval_runner_passes_without_plugins():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        runner = EvalRunner(project_root=root)
        verdict = runner.run(SAFE_DIFF, version="v1")
        assert verdict.passed is True
        plugin_checks = [c for c in verdict.checks if c.name.startswith("plugin:")]
        assert len(plugin_checks) == 0
