import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.state.schema import AgentState
from binarybyte.state.snapshots import load_snapshot, snapshot_state
from binarybyte.state.store import add_memory, read_state, write_state


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="rollback-test"), root)
    return root


def test_rollback_restores_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        add_memory("db", "PostgreSQL", project_root=root)
        snapshot_state("v1", root)

        add_memory("cache", "Redis", project_root=root)
        add_memory("queue", "RabbitMQ", project_root=root)
        current = read_state(root)
        assert len(current.memory) == 3

        old_state = load_snapshot("v1", root)
        write_state(old_state, root)
        restored = read_state(root)
        assert len(restored.memory) == 1
        assert restored.memory[0].key == "db"


def test_snapshot_isolation():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)

        add_memory("a", "1", project_root=root)
        snapshot_state("v1", root)

        add_memory("b", "2", project_root=root)
        snapshot_state("v2", root)

        v1 = load_snapshot("v1", root)
        v2 = load_snapshot("v2", root)

        assert len(v1.memory) == 1
        assert len(v2.memory) == 2
        assert v1.memory[0].key == "a"
        assert v2.memory[1].key == "b"
