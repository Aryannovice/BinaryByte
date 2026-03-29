from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binarybyte.core.config import load_config
from binarybyte.deploy.gate import check_gate, find_latest_version
from binarybyte.deploy.history import append_deploy_log, read_deploy_log
from binarybyte.deploy.manifest import get_adapter
from binarybyte.state.schema import AgentState
from binarybyte.state.snapshots import load_snapshot
from binarybyte.state.store import read_state

console = Console()


def _resolve_latest(version: str) -> str:
    if version != "latest":
        return version
    resolved = find_latest_version()
    if resolved is None:
        console.print(
            "[red]Error:[/red] No eval results found. "
            "Run 'binarybyte eval run --diff <file>' first."
        )
        raise SystemExit(1)
    return resolved


def _gate_check(version: str) -> None:
    console.print(f"Checking deploy gate for version [cyan]{version}[/cyan]...")
    try:
        verdict = check_gate(version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not verdict.passed:
        console.print(
            Panel(
                f"[red]Deploy blocked.[/red] Version '{version}' failed evaluation.\n"
                "Fix the issues and re-run eval before deploying.",
                border_style="red",
                title="Gate Check Failed",
            )
        )
        raise SystemExit(1)

    console.print("[green]Gate passed.[/green] Deploying to targets...\n")


def _deploy_to_targets(
    state: AgentState, version: str, rollback: bool = False,
) -> None:
    try:
        config = load_config()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    targets = config.agents.targets
    results: list[tuple[str, bool, str]] = []

    for target_name in targets:
        try:
            adapter = get_adapter(target_name)
            out_path = adapter.deploy(state, config)
            results.append((target_name, True, str(out_path)))
            console.print(f"  [green]OK[/green]  {target_name} -> {out_path}")
        except Exception as e:
            results.append((target_name, False, str(e)))
            console.print(f"  [red]FAIL[/red]  {target_name}: {e}")

    append_deploy_log(version, results, rollback=rollback)

    succeeded = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    status = "green" if succeeded == total else "yellow"
    label = "Rollback Complete" if rollback else "Deploy Complete"

    console.print(
        Panel(
            f"Deployed {succeeded}/{total} targets for version [cyan]{version}[/cyan].",
            border_style=status,
            title=label,
        )
    )


def run_deploy(version: str) -> None:
    try:
        state = read_state()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    version = _resolve_latest(version)
    _gate_check(version)
    _deploy_to_targets(state, version)


def run_deploy_rollback(version: str) -> None:
    try:
        snapshot = load_snapshot(version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    _gate_check(version)
    console.print(f"Rolling back to state snapshot from [cyan]{version}[/cyan]...\n")
    _deploy_to_targets(snapshot, version, rollback=True)


def run_deploy_history() -> None:
    log = read_deploy_log()
    if not log:
        console.print("[dim]No deploy history found.[/dim]")
        return

    table = Table(title="Deploy History")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Version", style="cyan")
    table.add_column("Timestamp", style="dim")
    table.add_column("Targets", style="white")
    table.add_column("Rollback", justify="center")

    for i, entry in enumerate(log, 1):
        targets_summary = ", ".join(
            f"[green]{k}[/green]" if v == "OK" else f"[red]{k}[/red]"
            for k, v in entry.get("targets", {}).items()
        )
        is_rollback = "[yellow]yes[/yellow]" if entry.get("rollback") else ""
        table.add_row(
            str(i),
            entry.get("version", "?"),
            entry.get("timestamp", "?")[:19],
            targets_summary,
            is_rollback,
        )

    console.print(table)
