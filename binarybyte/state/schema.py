from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    key: str
    value: str
    source: str = "manual"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentState(BaseModel):
    version: str = "1"
    project_name: str = ""
    conventions: list[str] = Field(default_factory=list)
    memory: list[MemoryEntry] = Field(default_factory=list)
