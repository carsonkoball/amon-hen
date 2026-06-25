import logging
import sys


def setup_logging(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
):
    """
    Logging helper to manage logs across scripts.
    """
    logging.basicConfig(
        level=level, format=format, handlers=[logging.StreamHandler(sys.stdout)]
    )
