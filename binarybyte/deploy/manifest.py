from __future__ import annotations

from pathlib import Path

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.deploy.targets.claude_code import ClaudeCodeAdapter
from binarybyte.deploy.targets.copilot import CopilotAdapter
from binarybyte.deploy.targets.cursor import CursorAdapter
from binarybyte.deploy.targets.gemini_cli import GeminiCliAdapter
from binarybyte.deploy.targets.windsurf import WindsurfAdapter
from binarybyte.core.constants import get_bb_dir
import importlib.util


_REGISTRY: dict[str, type[BaseAdapter]] = {
    "cursor": CursorAdapter,
    "gemini-cli": GeminiCliAdapter,
    "claude-code": ClaudeCodeAdapter,
    "windsurf": WindsurfAdapter,
    "copilot": CopilotAdapter,
}


def _load_plugins(project_root: Path | None = None) -> dict[str, type[BaseAdapter]]:
    registry: dict[str, type[BaseAdapter]] = {}
    plugins_dir = get_bb_dir(project_root) / "plugins"
    if not plugins_dir.exists():
        return registry

    for p in plugins_dir.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(p.stem, p)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                # find BaseAdapter subclasses
                for attr in dir(mod):
                    obj = getattr(mod, attr)
                    try:
                        if isinstance(obj, type) and issubclass(obj, BaseAdapter) and obj is not BaseAdapter:
                            name = getattr(obj, "NAME", p.stem)
                            registry[name] = obj
                    except Exception:
                        continue
        except Exception:
            continue

    return registry


def get_adapter(target: str, project_root: Path | None = None) -> BaseAdapter:
    cls = _REGISTRY.get(target)
    # load project plugins and merge
    plugins = _load_plugins(project_root)
    if target in plugins:
        cls = plugins[target]
    if cls is None:
        available = list(_REGISTRY.keys()) + list(plugins.keys())
        raise ValueError(
            f"Unknown deploy target '{target}'. "
            f"Available: {', '.join(available)}"
        )
    return cls(project_root=project_root)


def list_available_targets() -> list[str]:
    """List built-in deploy targets.

    Note: this intentionally returns only built-ins for backward compatibility.
    Use `list_all_targets()` or `list_plugin_targets()` to include project plugins.
    """

    return sorted(_REGISTRY.keys())


def list_built_in_targets() -> list[str]:
    """Alias for `list_available_targets()` with clearer semantics."""

    return list_available_targets()


def list_plugin_targets(project_root: Path | None = None) -> list[str]:
    """List deploy targets discovered from `.binarybyte/plugins/*.py` in a project."""

    return sorted(_load_plugins(project_root).keys())


def list_all_targets(project_root: Path | None = None) -> list[str]:
    """List all deploy targets: built-ins + project plugin adapters."""

    plugins = _load_plugins(project_root)
    return sorted(set(_REGISTRY.keys()) | set(plugins.keys()))
