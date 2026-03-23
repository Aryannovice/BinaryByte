import tempfile
from pathlib import Path

from binarybyte.state.schema import AgentState, MemoryEntry
from binarybyte.state.store import add_memory, read_state, write_state


def test_write_and_read_state_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        state = AgentState(project_name="test-proj")
        write_state(state, root)
        loaded = read_state(root)
        assert loaded.project_name == "test-proj"
        assert loaded.memory == []


def test_add_memory_appends_entry():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_state(AgentState(project_name="test"), root)
        entry = add_memory("db", "PostgreSQL", source="gemini-cli", project_root=root)
        assert entry.key == "db"
        assert entry.source == "gemini-cli"

        state = read_state(root)
        assert len(state.memory) == 1
        assert state.memory[0].key == "db"


def test_add_multiple_memory_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_state(AgentState(project_name="test"), root)
        add_memory("a", "val-a", project_root=root)
        add_memory("b", "val-b", project_root=root)
        add_memory("c", "val-c", project_root=root)

        state = read_state(root)
        assert len(state.memory) == 3
        keys = [e.key for e in state.memory]
        assert keys == ["a", "b", "c"]


def test_read_state_missing_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        try:
            read_state(root)
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_memory_entry_defaults():
    entry = MemoryEntry(key="k", value="v")
    assert entry.source == "manual"
    assert entry.timestamp is not None
