from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from binarybyte.core.config import BinaryByteConfig
from binarybyte.deploy.targets.base import BaseAdapter
from binarybyte.state.schema import AgentState


class CursorAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "cursor"

    def deploy(self, state: AgentState, config: BinaryByteConfig) -> Path:
        rules_dir = self.project_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        out_path = rules_dir / "binarybyte.mdc"

        sections: list[str] = []

        sections.append(dedent("""\
            ---
            description: BinaryByte — auto-generated agent rules. Do not edit manually.
            globs: "**/*"
            ---
        """))

        sections.append(f"# BinaryByte Rules for {state.project_name}\n")

        if state.conventions:
            sections.append("## Conventions\n")
            for conv in state.conventions:
                sections.append(f"- {conv}")
            sections.append("")

        if state.memory:
            sections.append("## Project Knowledge\n")
            for entry in state.memory:
                sections.append(f"- **{entry.key}**: {entry.value}")
            sections.append("")

        safety = config.eval.safety
        if safety.denied_commands or safety.denied_paths:
            sections.append("## Safety Rules\n")
            if safety.denied_commands:
                sections.append("Never use these commands:")
                for cmd in safety.denied_commands:
                    sections.append(f"- `{cmd}`")
                sections.append("")
            if safety.denied_paths:
                sections.append("Never modify these paths:")
                for p in safety.denied_paths:
                    sections.append(f"- `{p}`")
                sections.append("")

        out_path.write_text("\n".join(sections), encoding="utf-8")
        return out_path
