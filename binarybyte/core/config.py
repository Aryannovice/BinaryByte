from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from binarybyte.core.constants import get_config_path


class AgentsConfig(BaseModel):
    targets: list[str] = Field(default_factory=lambda: ["cursor", "gemini-cli"])


class SafetyEvalConfig(BaseModel):
    denied_commands: list[str] = Field(
        default_factory=lambda: ["rm -rf /", "DROP TABLE", "FORMAT", ":(){:|:&};:"]
    )
    denied_paths: list[str] = Field(
        default_factory=lambda: [".env", "secrets/", ".git/"]
    )


class EvalConfig(BaseModel):
    safety: SafetyEvalConfig = Field(default_factory=SafetyEvalConfig)


class StateConfig(BaseModel):
    conventions: list[str] = Field(default_factory=list)


class BinaryByteConfig(BaseModel):
    version: str = "1"
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    eval: EvalConfig = Field(default_factory=EvalConfig)
    state: StateConfig = Field(default_factory=StateConfig)


def default_config() -> BinaryByteConfig:
    return BinaryByteConfig()


def load_config(project_root: Path | None = None) -> BinaryByteConfig:
    path = get_config_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found at {path}. Run 'binarybyte init' first."
        )
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return BinaryByteConfig.model_validate(raw)


def save_config(config: BinaryByteConfig, project_root: Path | None = None) -> Path:
    path = get_config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            config.model_dump(),
            f,
            default_flow_style=False,
            sort_keys=False,
        )
    return path
