import tempfile
from pathlib import Path

from binarybyte.core.config import (
    BinaryByteConfig,
    default_config,
    load_config,
    save_config,
)


def test_default_config_has_expected_targets():
    config = default_config()
    assert "cursor" in config.agents.targets
    assert "gemini-cli" in config.agents.targets


def test_default_config_has_safety_rules():
    config = default_config()
    assert len(config.eval.safety.denied_commands) > 0
    assert len(config.eval.safety.denied_paths) > 0


def test_save_and_load_config_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        original = default_config()
        save_config(original, root)
        loaded = load_config(root)
        assert loaded.version == original.version
        assert loaded.agents.targets == original.agents.targets
        assert loaded.eval.safety.denied_commands == original.eval.safety.denied_commands


def test_load_config_missing_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        try:
            load_config(root)
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_config_model_validation():
    config = BinaryByteConfig.model_validate({
        "version": "2",
        "agents": {"targets": ["cursor"]},
        "eval": {"safety": {"denied_commands": ["rm -rf"], "denied_paths": []}},
        "state": {"conventions": ["use black"]},
    })
    assert config.version == "2"
    assert config.agents.targets == ["cursor"]
    assert config.eval.safety.denied_commands == ["rm -rf"]
    assert config.state.conventions == ["use black"]
