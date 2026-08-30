import json
import logging

from . import config
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging seup
logger = logging.getLogger(__name__)


def _get_fedramp_data():
    """
    Initiate GET request for FedRAMP marketplace listings and return the response in JSON format.
    """
    logger.debug("Fetching FedRAMP marketplace listings...")

    response = http_get(url=config.FEDRAMP_URL)

    data = response.json()

    logger.debug("Retrieved %d listings", len(data))

    return data["nodes"][3]["data"]


def _extract_listing_indices(data):
    indices = {}

    data_indices = data[0]["fedRAMPData"]
    data_indices = data[data_indices]["data"]
    data_indices = data[data_indices]

    for listing_type in config.LISTING_TYPES:
        listing_indices = data[data_indices[listing_type]]

        indices[listing_type] = listing_indices

    return indices


def _traverse(entry, data):
    if isinstance(entry, int):
        entry = data[entry]

    if isinstance(entry, list):
        return [_traverse(value, data) for value in entry]

    if isinstance(entry, dict):
        return {key: _traverse(value, data) for key, value in entry.items()}

    return entry


def _process_listing_index(data, listing_index):
    listing = data[listing_index].copy()

    for key in listing:
        entry = _traverse(listing[key], data)
        listing[key] = entry

    return listing


def _log_results(results, listing_type):
    """
    Log the results of the tracking process.
    """
    if results:
        for result in results:
            match result.label["type"]:
                case "products":
                    if result.is_new:
                        logger.info(
                            "%s listing %s added | csp: %s cso: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["csp"],
                            result.label["cso"],
                        )
                    elif result.is_removed:
                        logger.info(
                            "%s listing %s removed | csp: %s cso: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["csp"],
                            result.label["cso"],
                        )
                    else:
                        logger.info(
                            "%s listing %s modified | csp: %s cso: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["csp"],
                            result.label["cso"],
                        )
                case "agencies":
                    if result.is_new:
                        logger.info(
                            "%s listing %s added | parent: %s sub: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["parent"],
                            result.label["sub"],
                        )
                    elif result.is_removed:
                        logger.info(
                            "%s listing %s removed | parent: %s sub: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["parent"],
                            result.label["sub"],
                        )
                    else:
                        logger.info(
                            "%s listing %s modified | parent: %s sub: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["parent"],
                            result.label["sub"],
                        )
                case "assessors" | "advisors":
                    if result.is_new:
                        logger.info(
                            "%s listing %s added | name: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["name"],
                        )
                    elif result.is_removed:
                        logger.info(
                            "%s listing %s removed | name: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["csp"],
                        )
                    else:
                        logger.info(
                            "%s listing %s modified | name: %s",
                            result.label["type"],
                            result.identifier,
                            result.label["csp"],
                        )
    else:
        logger.info("no %s listing changes found", listing_type)


def _fedramp_tracker(tracker):
    products_records, agencies_records, assessors_records, advisors_records = (
        {},
        {},
        {},
        {},
    )

    data = _get_fedramp_data()

    listing_indices = _extract_listing_indices(data)

    # Iterate through every listing type
    for listing_type in listing_indices:
        # Iterate through every index of a listing type
        for index in listing_indices[listing_type]:
            listing = _process_listing_index(data, index)

            listing_id = listing["id"]

            match listing_type:
                case "Products":
                    label = {
                        "type": listing_type.lower(),
                        "csp": listing["csp"],
                        "cso": listing["cso"],
                    }
                    products_records[listing_id] = {
                        "id": listing_id,
                        "label": label,
                        "data": listing,
                    }
                case "Agencies":
                    label = {
                        "type": listing_type.lower(),
                        "parent": listing["parent"],
                        "sub": listing["sub"],
                    }
                    agencies_records[listing_id] = {
                        "id": listing_id,
                        "label": label,
                        "data": listing,
                    }
                case "Assessors":
                    label = {"type": listing_type.lower(), "name": listing["name"]}
                    assessors_records[listing_id] = {
                        "id": listing_id,
                        "label": label,
                        "data": listing,
                    }
                case "Advisors":
                    label = {"type": listing_type.lower(), "name": listing["name"]}
                    advisors_records[listing_id] = {
                        "id": listing_id,
                        "label": label,
                        "data": listing,
                    }

    products_results = tracker.track(
        records=products_records, path=config.LISTING_TYPE_DIR("products")
    )
    agencies_results = tracker.track(
        records=agencies_records, path=config.LISTING_TYPE_DIR("agencies")
    )
    assessors_results = tracker.track(
        records=assessors_records, path=config.LISTING_TYPE_DIR("assessors")
    )
    advisors_results = tracker.track(
        records=advisors_records, path=config.LISTING_TYPE_DIR("advisors")
    )

    _log_results(products_results, "products")
    _log_results(agencies_results, "agencies")
    _log_results(assessors_results, "assessors")
    _log_results(advisors_results, "advisors")

    return products_results, agencies_results, assessors_results, advisors_results


def run():
    """
    Execute the fedramp_tracker workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting fedramp_tracker")

    tracker = Tracker()

    products_results, agencies_results, assessors_results, advisors_results = (
        _fedramp_tracker(tracker=tracker)
    )

    logger.debug("Stopping fedramp_tracker")

    return products_results, agencies_results, assessors_results, advisors_results
