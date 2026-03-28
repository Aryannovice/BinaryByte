from __future__ import annotations

from typing import Optional
from rich.console import Console
from rich.panel import Panel

from binarybyte.cli.state_cmd import run_state_add, run_state_list
from binarybyte.cli.eval_cmd import run_eval
from binarybyte.cli.deploy_cmd import run_deploy

console = Console()


def _prompt(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        return ""


def run_interactive() -> None:
    console.print(Panel("BinaryByte Interactive — simple guided mode"))

    while True:
        console.print(
            "\nOptions:\n  1) Add state entry\n  2) List state\n  3) Evaluate patch file\n  4) Evaluate git range\n  5) Deploy latest\n  6) Exit"
        )
        choice = _prompt("Choose an option (1-6): ").strip()
        if choice == "1":
            key = _prompt("Key: ").strip()
            value = _prompt("Value: ").strip()
            source = _prompt("Source (manual): ").strip() or "manual"
            if key and value:
                run_state_add(key=key, value=value, source=source)
            else:
                console.print("[yellow]Skipped - key and value required.[/yellow]")
        elif choice == "2":
            run_state_list()
        elif choice == "3":
            path = _prompt("Patch file path: ").strip()
            if path:
                run_eval(diff=path, git_range=None, version="latest")
        elif choice == "4":
            rng = _prompt("Git range (e.g. HEAD~1..HEAD): ").strip()
            if rng:
                run_eval(diff=None, git_range=rng, version="latest")
        elif choice == "5":
            run_deploy(version="latest")
        else:
            console.print("Exiting interactive mode.")
            break
