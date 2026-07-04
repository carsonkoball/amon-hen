import logging
import sys


def setup_logging(
    format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level: int = logging.INFO,
) -> None:
    """
    Logging helper to manage logs across scripts.
    """
    logging.basicConfig(
        level=level, format=format, handlers=[logging.StreamHandler(sys.stdout)]
    )
