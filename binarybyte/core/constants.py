from pathlib import Path

BINARYBYTE_DIR = ".binarybyte"
CONFIG_FILE = "config.yaml"
STATE_FILE = "state.yaml"
RESULTS_DIR = "results"
PLUGINS_DIR = "plugins"
CHECKS_DIR = "checks"


def get_bb_dir(project_root: Path | None = None) -> Path:
    root = project_root or Path.cwd()
    return root / BINARYBYTE_DIR


def get_config_path(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / CONFIG_FILE


def get_state_path(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / STATE_FILE


def get_results_dir(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / RESULTS_DIR


def get_plugins_dir(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / PLUGINS_DIR


def get_checks_dir(project_root: Path | None = None) -> Path:
    return get_bb_dir(project_root) / CHECKS_DIR
