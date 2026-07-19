from pathlib import Path

from platformdirs import user_data_dir

from amon_hen.common.filesystem import ensure_dir

APP_NAME = "amon-hen"

DATA_DIR = Path(user_data_dir(APP_NAME))


def get_data_dir() -> Path:
    """
    Returns the root data directory.
    """
    ensure_dir(DATA_DIR)

    return DATA_DIR


def get_script_data_dir(tool_name: str) -> Path:
    """
    Returns the data directory for a specific script.
    """
    path = get_data_dir() / tool_name
    ensure_dir(path)

    return path
