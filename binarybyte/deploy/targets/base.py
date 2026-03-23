from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class BaseAdapter(ABC):
    """Abstract base for all agent deploy adapters."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifier used in config targets list (e.g. 'cursor', 'gemini-cli')."""
        ...

    @abstractmethod
    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        """Write the agent-specific config and return the path written."""
        ...
