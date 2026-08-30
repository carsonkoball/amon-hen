from datetime import datetime, UTC
from hashlib import sha256
import json
import logging

from . import config
from amon_hen.common.filesystem import ensure_dir, ensure_file, setup_environment
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging seup
logger = logging.getLogger(__name__)


def _get_listings():
    """
    Initiate GET request for DCMA blue list and return the response in JSON format.
    """
    logger.debug("Fetching DCMA blue list...")

    response = http_get(config.LISTINGS_URL)

    listings = response.json()

    logger.debug("Retrieved %d listings", len(listings))

    return listings


def _log_results(results):
    """
    Log the results of the tracking process.
    """
    if results:
        for result in results:
            if result.is_new:
                logger.info(
                    "listing %s added | manufacturer: %s product_name: %s product_type: %s",
                    result.identifier,
                    result.label["manufacturer"],
                    result.label["product_name"],
                    result.label["product_type"],
                )
            elif result.is_removed:
                logger.info(
                    "listing %s removed | manufacturer: %s product_name: %s product_type: %s",
                    result.identifier,
                    result.label["manufacturer"],
                    result.label["product_name"],
                    result.label["product_type"],
                )
            else:
                logger.info(
                    "listing %s modified | manufacturer: %s product_name: %s product_type: %s",
                    result.identifier,
                    result.label["manufacturer"],
                    result.label["product_name"],
                    result.label["product_type"],
                )
    else:
        logger.info("no listing changes found")


def blue_list_tracker(tracker):
    """
    Find blue list changes and return them.
    """
    records = {}

    listings = _get_listings()

    for listing in listings:
        listing_id = listing["UXSCore"]["mad_uxscoreid"]

        label = {
            "manufacturer": listing["manufacturer"]["mad_id"],
            "product_name": listing["UXSCore"]["mad_id"],
            "product_type": listing["UXSCore"]["mad_coretype"],
        }

        records[external_job_id] = {"label": label, "data": listing}

    results = tracker.track(records=records, path=config.DATA_DIR)

    _log_results(results)

    return results


def run():
    """
    Execute the blue_list_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting blue_list_tracker")

    results = blue_list_tracker(tracker=tracker)

    logger.debug("Stopping blue_list_tracker")

    return results
