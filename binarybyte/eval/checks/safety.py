from __future__ import annotations

import re

from binarybyte.core.config import BinaryByteConfig
from binarybyte.eval.schema import CheckResult


def _parse_added_lines(diff_text: str) -> list[str]:
    """Extract lines that were added (start with '+' but not '+++')."""
    added = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    return added


def _parse_changed_files(diff_text: str) -> list[str]:
    """Extract file paths from diff headers ('+++ b/path')."""
    files = []
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[6:])
        elif line.startswith("+++ "):
            files.append(line[4:])
    return files


def check_denied_commands(diff_text: str, config: BinaryByteConfig) -> CheckResult:
    denied = config.eval.safety.denied_commands
    added_lines = _parse_added_lines(diff_text)
    violations: list[str] = []

    for cmd in denied:
        pattern = re.escape(cmd)
        for i, line in enumerate(added_lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(f"Denied command '{cmd}' found in added line {i}: {line.strip()}")

    return CheckResult(
        name="denied_commands",
        passed=len(violations) == 0,
        details=violations if violations else ["No denied commands detected."],
    )


def check_denied_paths(diff_text: str, config: BinaryByteConfig) -> CheckResult:
    denied = config.eval.safety.denied_paths
    changed_files = _parse_changed_files(diff_text)
    violations: list[str] = []

    for path in changed_files:
        for denied_path in denied:
            normalized = denied_path.rstrip("/")
            if path == normalized or path.startswith(normalized + "/") or path.startswith(normalized):
                violations.append(f"Denied path modified: '{path}' matches rule '{denied_path}'")

    return CheckResult(
        name="denied_paths",
        passed=len(violations) == 0,
        details=violations if violations else ["No denied paths modified."],
    )
