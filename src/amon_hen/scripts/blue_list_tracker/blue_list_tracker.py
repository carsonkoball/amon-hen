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

    timestamp = datetime.now()

    response = http_get(config.LISTINGS_URL)

    listings = response.json()

    logger.debug("Retrieved %d listings", len(listings))

    return listings, timestamp


def _append_to(entry, path):
    """
    Save an entry to an append-only JSONL file.
    """
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(obj=entry) + "\n")


def _save_active(current_active):
    """
    Save IDs to the active.json file.
    """
    listings_active_path = config.LISTINGS_ACTIVE_FILE

    with open(file=listings_active_path, mode="w", encoding="utf-8") as file:
        json.dump(obj=sorted(current_active), fp=file, indent=2)


def _load_active():
    """
    Load IDs from the active.json file.
    """
    listings_active_path = config.LISTINGS_ACTIVE_FILE
    ensure_file(path=listings_active_path, default_content="[]")

    with open(file=listings_active_path, mode="r", encoding="utf-8") as file:
        previous_active = set(json.load(file))

    return previous_active


def blue_list_tracker(tracker):
    """
    Find blue list changes and return them.
    """
    results = []

    listings, timestamp = _get_listings()

    current_active = set()

    for listing in listings:
        listing_id = listing["UXSCore"]["mad_uxscoreid"]

        current_active.add(listing_id)

        listing_path = config.LISTING_DIR(listing_id)

        result = tracker.track(data=listing, path=listing_path)

        # Modified listing
        if result.has_changed:
            results.append(result)

            # New listing
            if result.is_new:
                # Mark as newly added in history
                listings_history_file_path = config.LISTINGS_HISTORY_FILE

                entry = config.HISTORY_ENTRY(
                    timestamp=timestamp.strftime("%Y-%m-%dT%H-%M-%S.%fZ"),
                    listing_id=listing_id,
                    listing_info={
                        "manufacturer": result.new_data["manufacturer"]["mad_id"],
                        "product_type": result.new_data["UXSCore"]["mad_coretype"],
                        "product_name": result.new_data["UXSCore"]["mad_id"],
                    },
                    event="added",
                )

                _append_to(entry=entry, path=listings_history_file_path)

    # Load previously active listings
    previous_active = _load_active()

    # Save current active listings
    _save_active(current_active=current_active)

    # Determine removed listings
    removed = previous_active - current_active

    # Every listing found to be removed
    for listing_id in removed:
        listing_path = config.LISTING_DIR(listing_id)

        result = tracker.track(data=None, path=listing_path)

        # Mark as removed in history
        listings_history_file_path = config.LISTINGS_HISTORY_FILE

        entry = config.HISTORY_ENTRY(
            timestamp=timestamp.strftime("%Y-%m-%dT%H-%M-%S.%fZ"),
            listing_id=listing_id,
            listing_info={
                "manufacturer": result.old_data["manufacturer"]["mad_id"],
                "product_type": result.old_data["UXSCore"]["mad_coretype"],
                "product_name": result.old_data["UXSCore"]["mad_id"],
            },
            event="added",
        )

        _append_to(entry=entry, path=listings_history_file_path)

        results.append(result)

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
