import logging
from pathlib import Path

# Logging setup
logger = logging.getLogger(__name__)


def ensure_dir(path):
    """
    Creates a directory given the path if it does not exist.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

        logger.debug("Created directory: %s", path)


def ensure_file(path):
    """
    Creates a valid file given the path if it doesn't exist.
    """
    ensure_dir(path.parent)

    if not path.exists():
        content = ""

        path.write_text(content)

        logger.debug("Created file: %s", path)


def setup_environment(directories, files):
    """
    Convenience wrapper to create script environment.
    """
    # Directory setup
    for directory in directories.values():
        ensure_dir(directory)

    logger.debug("Directories setup")

    # File setup
    for file in files.values():
        ensure_file(file)

    logger.debug("Files setup")
