from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from binarybyte.core.config import default_config, save_config
from binarybyte.core.constants import get_bb_dir
from binarybyte.state.schema import AgentState
from binarybyte.state.store import write_state

console = Console()


def run_init(project_dir: str) -> None:
    root = Path(project_dir).resolve()

    bb_dir = get_bb_dir(root)
    if bb_dir.exists():
        console.print(f"[yellow]Already initialized:[/yellow] {bb_dir}")
        return

    config = default_config()
    config_path = save_config(config, root)

    project_name = root.name
    state = AgentState(project_name=project_name)
    state_path = write_state(state, root)

    console.print(
        Panel(
            f"[green]Initialized BinaryByte in[/green] {bb_dir}\n\n"
            f"  Config:  {config_path.relative_to(root)}\n"
            f"  State:   {state_path.relative_to(root)}\n\n"
            f"  Project: {project_name}\n"
            f"  Targets: {', '.join(config.agents.targets)}\n\n"
            "Next steps:\n"
            "  binarybyte state add --key 'convention' --value 'Use pytest for tests'\n"
            "  binarybyte eval run --diff changes.patch\n"
            "  binarybyte deploy run",
            title="BinaryByte",
            border_style="blue",
        )
    )
