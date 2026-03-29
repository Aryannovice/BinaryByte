from __future__ import annotations

import importlib.util
from pathlib import Path

from binarybyte.core.config import BinaryByteConfig
from binarybyte.core.constants import get_checks_dir
from binarybyte.eval.schema import CheckResult


def load_eval_plugins(
    diff_text: str,
    config: BinaryByteConfig,
    project_root: Path | None = None,
) -> list[CheckResult]:
    """Discover and run user-defined eval checks from .binarybyte/checks/*.py.

    Each plugin file should export a function with the signature:
        def check(diff_text: str, config: BinaryByteConfig) -> CheckResult
    """
    checks_dir = get_checks_dir(project_root)
    if not checks_dir.exists():
        return []

    results: list[CheckResult] = []

    for p in sorted(checks_dir.glob("*.py")):
        try:
            spec = importlib.util.spec_from_file_location(f"bb_check_{p.stem}", p)
            if not spec or not spec.loader:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            check_fn = getattr(mod, "check", None)
            if check_fn is None or not callable(check_fn):
                results.append(CheckResult(
                    name=f"plugin:{p.stem}",
                    passed=False,
                    details=[f"Plugin '{p.name}' has no callable 'check' function."],
                ))
                continue

            result = check_fn(diff_text, config)
            if isinstance(result, CheckResult):
                if not result.name.startswith("plugin:"):
                    result.name = f"plugin:{result.name}"
                results.append(result)
            else:
                results.append(CheckResult(
                    name=f"plugin:{p.stem}",
                    passed=False,
                    details=[f"Plugin '{p.name}' check() did not return a CheckResult."],
                ))
        except Exception as e:
            results.append(CheckResult(
                name=f"plugin:{p.stem}",
                passed=False,
                details=[f"Plugin '{p.name}' raised an error: {e}"],
            ))

    return results
