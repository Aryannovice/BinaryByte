from rich.console import Console
from rich.table import Table

from binarybyte.state.store import add_memory, read_state

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
