import typer
from typing import Optional
from rich.console import Console

from binarybyte import __version__

app = typer.Typer(
    name="binarybyte",
    help="Infrastructure layer for AI coding agents — evaluate, sync, and deploy agent configs across tools.",
    no_args_is_help=True,
)
console = Console()

state_app = typer.Typer(help="Manage shared agent state (the canonical notebook).")
eval_app = typer.Typer(help="Evaluate agent changes for safety and correctness.")
deploy_app = typer.Typer(help="Deploy verified configs to target agents.")

app.add_typer(state_app, name="state")
app.add_typer(eval_app, name="eval")
app.add_typer(deploy_app, name="deploy")


def version_callback(value: bool) -> None:
    if value:
        console.print(f"binarybyte {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit.", callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """BinaryByte — the infrastructure layer for AI coding agents."""


@app.command()
def init(
    project_dir: str = typer.Argument(".", help="Project root directory (defaults to current)."),
) -> None:
    """Initialize BinaryByte in a project directory."""
    from binarybyte.cli.init_cmd import run_init

    run_init(project_dir)


@state_app.command("add")
def state_add(
    key: str = typer.Option(..., "--key", "-k", help="Memory entry key."),
    value: str = typer.Option(..., "--value", "-V", help="Memory entry value."),
    source: str = typer.Option("manual", "--source", "-s", help="Source agent or 'manual'."),
) -> None:
    """Add a memory entry to the shared state."""
    from binarybyte.cli.state_cmd import run_state_add

    run_state_add(key, value, source)


@state_app.command("list")
def state_list() -> None:
    """List all memory entries in the shared state."""
    from binarybyte.cli.state_cmd import run_state_list

    run_state_list()


@state_app.command("rollback")
def state_rollback(
    version: str = typer.Option(..., "--version", "-V", help="Version to roll back to."),
) -> None:
    """Roll back state to a previous eval snapshot."""
    from binarybyte.cli.state_cmd import run_state_rollback

    run_state_rollback(version)


@state_app.command("snapshots")
def state_snapshots() -> None:
    """List all available state snapshots."""
    from binarybyte.cli.state_cmd import run_state_snapshots

    run_state_snapshots()


@state_app.command("diff")
def state_diff(
    from_version: str = typer.Option(..., "--from", help="Source version to compare from."),
    to_version: str = typer.Option(..., "--to", help="Target version to compare to."),
) -> None:
    """Compare state between two eval snapshots."""
    from binarybyte.cli.state_cmd import run_state_diff

    run_state_diff(from_version, to_version)


@eval_app.command("run")
def eval_run(
    diff: Optional[str] = typer.Option(None, "--diff", "-d", help="Path to a unified diff / patch file."),
    git_range: Optional[str] = typer.Option(None, "--git-range", help="Git range to diff (e.g. HEAD~1..HEAD)."),
    version: str = typer.Option("latest", "--version", "-V", help="Version label for this eval."),
) -> None:
    """Run evaluation checks against a diff."""
    from binarybyte.cli.eval_cmd import run_eval

    run_eval(diff=diff, git_range=git_range, version=version)


@app.command()
def interactive() -> None:
    """Start interactive guided mode for non-technical users."""
    from binarybyte.cli.interactive_cmd import run_interactive

    run_interactive()


@deploy_app.command("run")
def deploy_run(
    version: str = typer.Option("latest", "--version", "-V", help="Version to deploy."),
) -> None:
    """Deploy verified agent configs to all targets."""
    from binarybyte.cli.deploy_cmd import run_deploy

    run_deploy(version)


@deploy_app.command("rollback")
def deploy_rollback(
    version: str = typer.Option(..., "--version", "-V", help="Version to roll back to."),
) -> None:
    """Roll back deployment to a previous state snapshot."""
    from binarybyte.cli.deploy_cmd import run_deploy_rollback

    run_deploy_rollback(version)


@deploy_app.command("history")
def deploy_history() -> None:
    """Show deployment history log."""
    from binarybyte.cli.deploy_cmd import run_deploy_history

    run_deploy_history()


@deploy_app.command("targets")
def deploy_targets() -> None:
    """List available deploy targets (built-ins + project plugins)."""
    from binarybyte.cli.deploy_cmd import run_deploy_targets

    run_deploy_targets()


if __name__ == "__main__":
    app()
