from __future__ import annotations

import re

from binarybyte.core.config import BinaryByteConfig
from binarybyte.eval.schema import CheckResult

_DEFAULT_SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
    r"ghp_[a-zA-Z0-9]{36}",
    r"gho_[a-zA-Z0-9]{36}",
    r"github_pat_[a-zA-Z0-9_]{22,}",
    r"sk-[a-zA-Z0-9]{20,}",
    r"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
]


def _parse_added_lines(diff_text: str) -> list[tuple[int, str]]:
    numbered: list[tuple[int, str]] = []
    idx = 0
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            idx += 1
            numbered.append((idx, line[1:]))
    return numbered


def check_secrets(diff_text: str, config: BinaryByteConfig) -> CheckResult:
    if not config.eval.safety.scan_secrets:
        return CheckResult(
            name="secret_detection",
            passed=True,
            details=["Secret scanning is disabled."],
        )

    patterns = config.eval.safety.secret_patterns
    if not patterns:
        patterns = list(_DEFAULT_SECRET_PATTERNS)

    added_lines = _parse_added_lines(diff_text)
    violations: list[str] = []

    for pattern in patterns:
        compiled = re.compile(pattern)
        for line_num, line in added_lines:
            if compiled.search(line):
                masked = line.strip()
                if len(masked) > 80:
                    masked = masked[:77] + "..."
                violations.append(
                    f"Potential secret at added line {line_num}: {masked}"
                )

    return CheckResult(
        name="secret_detection",
        passed=len(violations) == 0,
        details=violations if violations else ["No secrets detected in diff."],
    )
