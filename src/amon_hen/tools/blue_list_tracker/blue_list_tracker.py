import json
import logging

from . import config
from amon_hen.common.http import http_post
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging seup
logger = logging.getLogger(__name__)


def _get_listings():
    """
    Initiate POST requests for DCMA Blue Cleared and Framework lists and return the responses in JSON format.
    """
    logger.debug("Fetching X-UserToken-Response header value...")

    # Used to get relevant header value
    init_response = http_post(url=config.BLUE_LIST_URL, json=config.CLEARED_DATA)

    header = {"X-UserToken": init_response.headers["X-UserToken-Response"]}

    logger.debug("Retrieved value of %s", header["X-UserToken"])
    logger.debug("Fetching DMCA Blue Cleared List...")

    # Cleared listings
    cleared_response = http_post(
        url=config.BLUE_LIST_URL,
        json=config.CLEARED_DATA,
        params=config.CLEARED_PARAMS,
        headers=header,
    ).json()

    logger.debug(
        "Retrieved %d listings", len(cleared_response["result"]["data"]["list"])
    )
    logger.debug("Fetching DMCA Blue Framework List...")

    # Framework listings
    framework_response = http_post(
        url=config.BLUE_LIST_URL,
        json=config.FRAMEWORK_DATA,
        params=config.FRAMEWORK_PARAMS,
        headers=header,
    ).json()

    logger.debug(
        "Retrieved %d listings", len(framework_response["result"]["data"]["list"])
    )

    return cleared_response, framework_response


def _log_results(results, listing_type):
    """
    Log the results of the tracking process.
    """
    if not results:
        logger.info("no %s listing changes found", listing_type)
    if results:
        for result in results:
            if result.is_new:
                status = "added"
            elif result.is_removed:
                status = "removed"
            else:
                status = "modified"

            logger.info(
                "%s listing %s %s | manufacturer: %s cmdb_model_category: %s name: %s",
                result.label["list"],
                result.identifier,
                status,
                result.label["manufacturer"],
                result.label["cmdb_model_category"],
                result.label["name"],
            )


def _blue_list_tracker(tracker):
    """
    Find blue list changes and return them.
    """
    cleared_records, framework_records = {}, {}

    cleared_listings, framework_listings = _get_listings()
    cleared_listings = cleared_listings["result"]["data"]["list"]
    framework_listings = framework_listings["result"]["data"]["list"]

    # Process Cleared List listings
    for listing in cleared_listings:
        listing_id = listing["sys_id"]

        label = {
            "list": "cleared",
            "manufacturer": listing["manufacturer"]["display_value"],
            "cmdb_model_category": listing["cmdb_model_category"]["display_value"],
            "name": listing["name"]["display_value"],
        }

        cleared_records[listing_id] = {"label": label, "data": listing}

    # Process Framework List listings
    for listing in framework_listings:
        listing_id = listing["sys_id"]

        label = {
            "list": "framework",
            "manufacturer": listing["manufacturer"]["display_value"],
            "cmdb_model_category": listing["cmdb_model_category"]["display_value"],
            "name": listing["name"]["display_value"],
        }

        framework_records[listing_id] = {"label": label, "data": listing}

    cleared_results = tracker.track(records=cleared_records, path=config.CLEARED_DIR)
    framework_results = tracker.track(
        records=framework_records, path=config.FRAMEWORK_DIR
    )

    _log_results(cleared_results, "cleared")
    _log_results(framework_results, "framework")

    return cleared_results, framework_results


def run():
    """
    Execute the blue_list_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting blue_list_tracker")

    cleared_results, framework_results = _blue_list_tracker(tracker=tracker)

    logger.debug("Stopping blue_list_tracker")

    return cleared_results, framework_results
