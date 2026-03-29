import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.eval.runner import EvalRunner
from binarybyte.state.schema import AgentState
from binarybyte.state.snapshots import (
    list_snapshots,
    load_snapshot,
    snapshot_state,
)
from binarybyte.state.store import add_memory, write_state

SAFE_DIFF = """\
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,3 @@
+import os
 def main():
-    pass
+    print("hello")
"""


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="snap-test"), root)
    return root


def test_snapshot_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        path = snapshot_state("v1", root)
        assert path.exists()
        assert path.name == "state_snapshot.yaml"


def test_load_snapshot_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        add_memory("lang", "Python", project_root=root)
        snapshot_state("v1", root)
        loaded = load_snapshot("v1", root)
        assert loaded.project_name == "snap-test"
        assert len(loaded.memory) == 1
        assert loaded.memory[0].key == "lang"


def test_load_snapshot_missing_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        try:
            load_snapshot("nonexistent", root)
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_list_snapshots_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        assert list_snapshots(root) == []


def test_list_snapshots_multiple():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        snapshot_state("v1", root)
        snapshot_state("v2", root)
        snaps = list_snapshots(root)
        assert "v1" in snaps
        assert "v2" in snaps


def test_eval_runner_creates_snapshot():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        runner = EvalRunner(project_root=root)
        runner.run(SAFE_DIFF, version="v1")
        snap_path = root / ".binarybyte" / "results" / "v1" / "state_snapshot.yaml"
        assert snap_path.exists()


def test_snapshot_preserves_state_at_eval_time():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        add_memory("db", "PostgreSQL", project_root=root)
        runner = EvalRunner(project_root=root)
        runner.run(SAFE_DIFF, version="v1")

        add_memory("cache", "Redis", project_root=root)

        snapshot = load_snapshot("v1", root)
        assert len(snapshot.memory) == 1
        assert snapshot.memory[0].key == "db"
