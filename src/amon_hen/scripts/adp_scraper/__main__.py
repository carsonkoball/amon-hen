import logging

from . import config
from .adp_scraper import adp_scraper
from amon_hen.common.log_config import setup_logging
from amon_hen.common.filesystem import ensure_dir, ensure_file

# Logging setup
logger = logging.getLogger(__name__)


def main():
    setup_logging()

    # Directory setup
    ensure_dir(config.DATA_DIR)
    ensure_dir(config.LOG_DIR)
    ensure_dir(config.ARCHIVE_DIR)

    # File setup
    ensure_file(config.ACTIVE_FILE, default_content="{}")
    ensure_file(config.REMOVED_FILE, default_content="{}")
    ensure_file(config.LOG_FILE)

    logger.debug("Starting adp_scraper")

    adp_scraper()

    logger.debug("Stopping adp_scraper")


if __name__ == "__main__":
    main()
