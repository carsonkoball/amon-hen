from collections.abc import Mapping
import logging
from pathlib import Path
from typing import Any

# Logging setup
logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> bool:
    """
    Creates a directory given the path if it does not already exist.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

        logger.debug("Created directory: %s", path)

        return False

    return True


def ensure_file(path: Path, default_content: str = "") -> bool:
    """
    Creates a valid file given the path if it does not already exist.
    """
    ensure_dir(path.parent)

    if not path.exists():
        path.write_text(default_content)

        logger.debug("Created file: %s", path)

        return False

    return True


def setup_environment(
    directories: Mapping[str, Path], files: Mapping[str, Path]
) -> tuple[dict[str, bool], dict[str, bool]]:
    """
    Convenience wrapper to create script environment.
    """
    directories_results = {}
    files_results = {}

    # Directory setup
    for directory in directories:
        directories_results[directory] = ensure_dir(directories[directory])

    logger.debug("Directories set up")

    # File setup
    for file in files:
        files_results[file] = ensure_file(files[file][0], files[file][1])

    logger.debug("Files set up")

    return directories_results, files_results
