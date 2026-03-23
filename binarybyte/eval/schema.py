from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    name: str
    passed: bool
    details: list[str] = Field(default_factory=list)


class Verdict(BaseModel):
    version: str
    passed: bool
    checks: list[CheckResult] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
