import tempfile
from pathlib import Path

from binarybyte.core.config import default_config, save_config
from binarybyte.deploy.manifest import get_adapter, list_available_targets
from binarybyte.deploy.targets.claude_code import ClaudeCodeAdapter
from binarybyte.deploy.targets.copilot import CopilotAdapter
from binarybyte.deploy.targets.windsurf import WindsurfAdapter
from binarybyte.state.schema import AgentState, MemoryEntry
from binarybyte.state.store import write_state


def _setup_project(tmpdir: str) -> Path:
    root = Path(tmpdir)
    save_config(default_config(), root)
    write_state(AgentState(project_name="adapter-test"), root)
    return root


def _make_state_with_memory() -> AgentState:
    state = AgentState(project_name="adapter-test")
    state.memory.append(MemoryEntry(key="lang", value="Python"))
    state.conventions = ["Use pytest", "Use type hints"]
    return state


def test_registry_includes_new_targets():
    targets = list_available_targets()
    assert "claude-code" in targets
    assert "windsurf" in targets
    assert "copilot" in targets
    assert "cursor" in targets
    assert "gemini-cli" in targets


def test_get_adapter_claude_code():
    adapter = get_adapter("claude-code")
    assert isinstance(adapter, ClaudeCodeAdapter)


def test_get_adapter_windsurf():
    adapter = get_adapter("windsurf")
    assert isinstance(adapter, WindsurfAdapter)


def test_get_adapter_copilot():
    adapter = get_adapter("copilot")
    assert isinstance(adapter, CopilotAdapter)


def test_claude_code_deploy():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        state = _make_state_with_memory()
        config = default_config()
        adapter = ClaudeCodeAdapter(project_root=root)
        path = adapter.deploy(state, config)
        assert path.exists()
        assert path.name == "CLAUDE.md"
        content = path.read_text()
        assert "BinaryByte Context" in content
        assert "lang" in content
        assert "Python" in content
        assert "Use pytest" in content


def test_windsurf_deploy():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        state = _make_state_with_memory()
        config = default_config()
        adapter = WindsurfAdapter(project_root=root)
        path = adapter.deploy(state, config)
        assert path.exists()
        assert path.name == ".windsurfrules"
        content = path.read_text()
        assert "BinaryByte Rules" in content
        assert "lang" in content
        assert "Use type hints" in content


def test_copilot_deploy():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = _setup_project(tmpdir)
        state = _make_state_with_memory()
        config = default_config()
        adapter = CopilotAdapter(project_root=root)
        path = adapter.deploy(state, config)
        assert path.exists()
        assert path.name == "copilot-instructions.md"
        assert (root / ".github").is_dir()
        content = path.read_text()
        assert "BinaryByte Instructions" in content
        assert "lang" in content


def test_copilot_creates_github_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assert not (root / ".github").exists()
        adapter = CopilotAdapter(project_root=root)
        state = AgentState(project_name="test")
        config = default_config()
        adapter.deploy(state, config)
        assert (root / ".github").is_dir()
