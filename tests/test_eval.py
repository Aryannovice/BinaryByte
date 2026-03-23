import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.eval.checks.imports import check_imports
from binarybyte.eval.checks.safety import check_denied_commands, check_denied_paths
from binarybyte.eval.runner import EvalRunner
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state

SAFE_DIFF = """\
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,4 @@
+import os
+import json
 def main():
-    pass
+    print("hello")
"""

UNSAFE_DIFF = """\
diff --git a/.env b/.env
--- a/.env
+++ b/.env
@@ -1 +1,2 @@
 DB_HOST=localhost
+DB_PASSWORD=secret
diff --git a/cleanup.sh b/cleanup.sh
--- a/cleanup.sh
+++ b/cleanup.sh
@@ -1 +1,2 @@
 #!/bin/bash
+rm -rf /
"""

HALLUCINATED_IMPORT_DIFF = """\
diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1,2 @@
+import totally_fake_nonexistent_pkg_xyz
 pass
"""


def test_denied_commands_pass():
    config = default_config()
    result = check_denied_commands(SAFE_DIFF, config)
    assert result.passed is True


def test_denied_commands_fail():
    config = default_config()
    result = check_denied_commands(UNSAFE_DIFF, config)
    assert result.passed is False
    assert any("rm -rf /" in d for d in result.details)


def test_denied_paths_pass():
    config = default_config()
    result = check_denied_paths(SAFE_DIFF, config)
    assert result.passed is True


def test_denied_paths_fail():
    config = default_config()
    result = check_denied_paths(UNSAFE_DIFF, config)
    assert result.passed is False
    assert any(".env" in d for d in result.details)


def test_imports_pass():
    result = check_imports(SAFE_DIFF)
    assert result.passed is True


def test_imports_fail_hallucinated():
    result = check_imports(HALLUCINATED_IMPORT_DIFF)
    assert result.passed is False
    assert any("totally_fake_nonexistent_pkg_xyz" in d for d in result.details)


def test_imports_empty_diff():
    result = check_imports("")
    assert result.passed is True


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="test"), root)
    return root


def test_eval_runner_pass():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        runner = EvalRunner(project_root=root)
        verdict = runner.run(SAFE_DIFF, version="v1")
        assert verdict.passed is True
        assert all(c.passed for c in verdict.checks)
        verdict_file = root / ".binarybyte" / "results" / "v1" / "verdict.json"
        assert verdict_file.exists()


def test_eval_runner_fail():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        runner = EvalRunner(project_root=root)
        verdict = runner.run(UNSAFE_DIFF, version="v2")
        assert verdict.passed is False
