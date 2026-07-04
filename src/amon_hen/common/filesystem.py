from collections.abc import Mapping
import logging
from pathlib import Path
from typing import Any

# Logging setup
logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> None:
    """
    Creates a directory given the path if it does not already exist.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

        logger.debug("Created directory: %s", path)


def ensure_file(path: Path, default_content: str = "") -> None:
    """
    Creates a valid file given the path if it does not already exist.
    """
    ensure_dir(path.parent)

    if not path.exists():
        path.write_text(default_content)

        logger.debug("Created file: %s", path)


def setup_environment(
    directories: Mapping[str, Path], files: Mapping[str, Path]
) -> None:
    """
    Convenience wrapper to create script environment.
    """
    # Directory setup
    for directory in directories.values():
        ensure_dir(directory)

    logger.debug("Directories set up")

    # File setup
    for file in files.values():
        ensure_file(file[0], file[1])

    logger.debug("Files set up")
