from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from binarybyte.core.config import SandboxConfig
from binarybyte.eval.schema import CheckResult


def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _apply_patch(project_dir: Path, diff_text: str, work_dir: Path) -> Path:
    """Copy the project to a temp directory and apply the diff."""
    dest = work_dir / "project"
    shutil.copytree(project_dir, dest, dirs_exist_ok=True)

    patch_file = work_dir / "changes.patch"
    patch_file.write_text(diff_text, encoding="utf-8")

    try:
        subprocess.run(
            ["git", "apply", "--allow-empty", str(patch_file)],
            cwd=str(dest),
            capture_output=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return dest


def run_sandbox(
    diff_text: str,
    sandbox_config: SandboxConfig,
    project_root: Path | None = None,
) -> list[CheckResult]:
    """Run sandbox evaluation using Docker.

    Returns a list of CheckResults, one per configured command.
    Gracefully degrades if Docker is unavailable.
    """
    if not sandbox_config.enabled:
        return []

    if not _docker_available():
        return [
            CheckResult(
                name="sandbox",
                passed=True,
                details=["Sandbox skipped: Docker is not available. Install Docker to enable sandbox evaluation."],
            )
        ]

    root = project_root or Path.cwd()
    results: list[CheckResult] = []

    with tempfile.TemporaryDirectory(prefix="bb_sandbox_") as tmpdir:
        work_dir = Path(tmpdir)
        patched = _apply_patch(root, diff_text, work_dir)

        for cmd in sandbox_config.commands:
            check_name = f"sandbox:{cmd.split()[0]}"
            try:
                proc = subprocess.run(
                    [
                        "docker", "run",
                        "--rm",
                        "--network=none",
                        "--memory=512m",
                        "--cpus=1",
                        "-v", f"{patched}:/workspace:ro",
                        "-w", "/workspace",
                        sandbox_config.image,
                        "sh", "-c", cmd,
                    ],
                    capture_output=True,
                    timeout=sandbox_config.timeout_seconds,
                )

                stdout = proc.stdout.decode("utf-8", errors="replace").strip()
                stderr = proc.stderr.decode("utf-8", errors="replace").strip()
                passed = proc.returncode == 0

                details: list[str] = []
                if passed:
                    details.append(f"Command '{cmd}' passed (exit code 0).")
                else:
                    details.append(f"Command '{cmd}' failed (exit code {proc.returncode}).")

                if stdout:
                    truncated = stdout[:500] + ("..." if len(stdout) > 500 else "")
                    details.append(f"stdout: {truncated}")
                if stderr:
                    truncated = stderr[:500] + ("..." if len(stderr) > 500 else "")
                    details.append(f"stderr: {truncated}")

                results.append(CheckResult(name=check_name, passed=passed, details=details))

            except subprocess.TimeoutExpired:
                results.append(CheckResult(
                    name=check_name,
                    passed=False,
                    details=[f"Command '{cmd}' timed out after {sandbox_config.timeout_seconds}s."],
                ))
            except Exception as e:
                results.append(CheckResult(
                    name=check_name,
                    passed=False,
                    details=[f"Sandbox error for '{cmd}': {e}"],
                ))

    return results
