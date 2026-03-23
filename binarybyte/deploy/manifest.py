from __future__ import annotations

from pathlib import Path

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.deploy.targets.cursor import CursorAdapter
from binarybyte.deploy.targets.gemini_cli import GeminiCliAdapter

_REGISTRY: dict[str, type[BaseAdapter]] = {
    "cursor": CursorAdapter,
    "gemini-cli": GeminiCliAdapter,
}


def get_adapter(target: str, project_root: Path | None = None) -> BaseAdapter:
    cls = _REGISTRY.get(target)
    if cls is None:
        raise ValueError(
            f"Unknown deploy target '{target}'. "
            f"Available: {', '.join(_REGISTRY.keys())}"
        )
    return cls(project_root=project_root)


def list_available_targets() -> list[str]:
    return list(_REGISTRY.keys())
