from rich.console import Console
from rich.panel import Panel

from binarybyte.core.config import load_config
from binarybyte.deploy.gate import check_gate, find_latest_version
from binarybyte.deploy.manifest import get_adapter
from binarybyte.state.store import read_state

console = Console()


def run_deploy(version: str) -> None:
    try:
        config = load_config()
        state = read_state()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if version == "latest":
        resolved = find_latest_version()
        if resolved is None:
            console.print(
                "[red]Error:[/red] No eval results found. "
                "Run 'binarybyte eval run --diff <file>' first."
            )
            raise SystemExit(1)
        version = resolved

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

    succeeded = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    status = "green" if succeeded == total else "yellow"

    console.print(
        Panel(
            f"Deployed {succeeded}/{total} targets for version [cyan]{version}[/cyan].",
            border_style=status,
            title="Deploy Complete",
        )
    )
