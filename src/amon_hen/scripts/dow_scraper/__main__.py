import logging

from . import config
from .dow_scraper import dow_scraper
from amon_hen.common.log_config import setup_logging
from amon_hen.common.filesystem import ensure_dir, ensure_file

# Logging setup
logger = logging.getLogger(__name__)


def main():
    setup_logging()

    # Directory setup
    ensure_dir(config.DATA_DIR)
    ensure_dir(config.LOG_DIR)

    # File setup
    ensure_file(config.LOG_FILE)

    logger.debug("Starting dow_scraper")

    dow_scraper()

    logger.debug("Stopping dow_scraper")


if __name__ == "__main__":
    main()
