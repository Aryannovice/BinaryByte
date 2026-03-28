"""Example deploy plugin for BinaryByte.

Copy this file into your project's `.binarybyte/plugins/` directory as
`example_adapter.py` to add a new deploy target named `example`.

The class should subclass `BaseAdapter` and provide a `NAME` attribute
used for discovery by BinaryByte's plugin loader.
"""
from pathlib import Path

from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.core.config import BinaryByteConfig
from binarybyte.state.schema import AgentState


class ExampleAdapter(BaseAdapter):
    NAME = "example"

    @property
    def name(self) -> str:
        return self.NAME

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        out_dir = self.project_root / ".example"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "binarybyte-example.txt"
        lines = [f"Project: {state.project_name}"]
        if state.conventions:
            lines.append("Conventions:")
            lines.extend(f"- {c}" for c in state.conventions)
        if state.memory:
            lines.append("Knowledge:")
            lines.extend(f"- {m.key}: {m.value}" for m in state.memory)
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
