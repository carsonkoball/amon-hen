import logging
from pathlib import Path

# Logging setup
logger = logging.getLogger(__name__)


def ensure_dir(path):
    """
    Creates a given directory if it does not exist.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("Created directory: %s", path)


def ensure_file(path, default_content=""):
    """
    Creates a given file if it doesn't exist and writes default content to it.
    """
    ensure_dir(path.parent)

    if not path.exists():
        path.write_text(default_content)
        logger.debug("Created file: %s", path)
