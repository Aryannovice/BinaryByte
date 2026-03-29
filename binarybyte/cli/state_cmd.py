from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binarybyte.state.snapshots import list_snapshots, load_snapshot
from binarybyte.state.store import add_memory, read_state, write_state

console = Console()


def run_state_add(key: str, value: str, source: str) -> None:
    try:
        entry = add_memory(key=key, value=value, source=source)
        console.print(
            f"[green]Added:[/green] {entry.key} = {entry.value} "
            f"[dim](source: {entry.source})[/dim]"
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


def run_state_list() -> None:
    try:
        state = read_state()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    console.print(f"[bold]Project:[/bold] {state.project_name}")
    console.print(f"[bold]Version:[/bold] {state.version}\n")

    if state.conventions:
        console.print("[bold]Conventions:[/bold]")
        for conv in state.conventions:
            console.print(f"  - {conv}")
        console.print()

    if not state.memory:
        console.print("[dim]No memory entries yet. Use 'binarybyte state add' to add one.[/dim]")
        return

    table = Table(title="Memory Entries")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Source", style="green")
    table.add_column("Timestamp", style="dim")

    for entry in state.memory:
        table.add_row(
            entry.key,
            entry.value,
            entry.source,
            entry.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

    console.print(table)


def run_state_rollback(version: str) -> None:
    try:
        snapshot = load_snapshot(version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    write_state(snapshot)
    console.print(
        Panel(
            f"[green]State rolled back to version[/green] [cyan]{version}[/cyan]\n"
            f"  Project:  {snapshot.project_name}\n"
            f"  Memory:   {len(snapshot.memory)} entries\n"
            f"  Conventions: {len(snapshot.conventions)} items",
            border_style="green",
            title="State Rollback",
        )
    )


def run_state_snapshots() -> None:
    versions = list_snapshots()
    if not versions:
        console.print("[dim]No state snapshots found. Run 'binarybyte eval run' to create one.[/dim]")
        return

    table = Table(title="State Snapshots")
    table.add_column("Version", style="cyan")
    table.add_column("Memory Entries", justify="center")
    table.add_column("Conventions", justify="center")

    for ver in versions:
        try:
            snap = load_snapshot(ver)
            table.add_row(ver, str(len(snap.memory)), str(len(snap.conventions)))
        except Exception:
            table.add_row(ver, "[red]error[/red]", "[red]error[/red]")

    console.print(table)


def run_state_diff(from_version: str, to_version: str) -> None:
    try:
        from_state = load_snapshot(from_version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    try:
        to_state = load_snapshot(to_version)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    from_keys = {e.key: e.value for e in from_state.memory}
    to_keys = {e.key: e.value for e in to_state.memory}

    all_keys = sorted(set(from_keys) | set(to_keys))

    if not all_keys and from_state.conventions == to_state.conventions:
        console.print("[dim]No differences found.[/dim]")
        return

    table = Table(title=f"State Diff: {from_version} → {to_version}")
    table.add_column("Key", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column(f"{from_version}", style="dim")
    table.add_column(f"{to_version}", style="white")

    for key in all_keys:
        in_from = key in from_keys
        in_to = key in to_keys
        if in_from and in_to:
            if from_keys[key] != to_keys[key]:
                table.add_row(key, "[yellow]CHANGED[/yellow]", from_keys[key], to_keys[key])
        elif in_to:
            table.add_row(key, "[green]ADDED[/green]", "", to_keys[key])
        else:
            table.add_row(key, "[red]REMOVED[/red]", from_keys[key], "")

    console.print(table)

    from_convs = set(from_state.conventions)
    to_convs = set(to_state.conventions)
    added_convs = to_convs - from_convs
    removed_convs = from_convs - to_convs

    if added_convs or removed_convs:
        console.print("\n[bold]Convention changes:[/bold]")
        for c in sorted(added_convs):
            console.print(f"  [green]+ {c}[/green]")
        for c in sorted(removed_convs):
            console.print(f"  [red]- {c}[/red]")
