from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binarybyte.eval.runner import EvalRunner

console = Console()


def run_eval(diff: str, version: str) -> None:
    diff_path = Path(diff)
    if not diff_path.exists():
        console.print(f"[red]Error:[/red] Diff file not found: {diff}")
        raise SystemExit(1)

    diff_text = diff_path.read_text(encoding="utf-8")
    if not diff_text.strip():
        console.print("[yellow]Warning:[/yellow] Diff file is empty.")
        return

    try:
        runner = EvalRunner()
        verdict = runner.run(diff_text, version=version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    table = Table(title="Evaluation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")

    for check in verdict.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        details = "\n".join(check.details[:3])
        if len(check.details) > 3:
            details += f"\n... and {len(check.details) - 3} more"
        table.add_row(check.name, status, details)

    console.print(table)

    overall = "[bold green]PASSED[/bold green]" if verdict.passed else "[bold red]FAILED[/bold red]"
    console.print(
        Panel(
            f"Verdict: {overall}\n"
            f"Version: {verdict.version}\n"
            f"Checks:  {sum(c.passed for c in verdict.checks)}/{len(verdict.checks)} passed",
            border_style="green" if verdict.passed else "red",
        )
    )
