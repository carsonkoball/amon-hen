from datetime import datetime, UTC
from hashlib import sha256
import json
import logging

from . import config
from amon_hen.common.filesystem import ensure_dir, ensure_file, setup_environment
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging

# Logging seup
logger = logging.getLogger(__name__)


def get_listings():
    """
    Initiate GET request for DCMA blue list and return the response in JSON format.
    """
    logger.debug("Fetching DCMA blue list...")

    response = http_get(config.LISTINGS_URL)

    listings = response.json()

    logger.debug("Retrieved %d listings", len(listings))

    return listings


def load_metadata(listing_id):
    """
    Load metadata file for listing into dictionary if it exists.
    If it doesn't exist, create a new metadata file and return empty dictionary.
    """
    listing_dir_path = config.LISTING_DIR(listing_id)
    metadata_file_path = config.METADATA_FILE(listing_id)

    ensure_dir(listing_dir_path)
    existed = ensure_file(metadata_file_path, "{}")

    if not existed:
        logger.debug("Created metadata for listing %s", listing_id)

    metadata = {}
    with open(metadata_file_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return metadata, existed


def save_metadata(metadata, listing_id):
    """
    Save metadata dictionary into metadata file for listing.
    """
    metadata_file_path = config.METADATA_FILE(listing_id)
    temporary_file_path = metadata_file_path.with_suffix(".tmp")

    with open(temporary_file_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    temporary_file_path.replace(metadata_file_path)


def load_listing(listing_id):
    """
    Load listing file into dictionary.
    """
    metadata, _ = load_metadata(listing_id)

    timestamp = metadata["last_updated"]
    listing_file_path = config.LISTING_FILE(listing_id, timestamp)

    listing = {}
    with open(listing_file_path, "r", encoding="utf-8") as file:
        listing = json.load(file)

    return listing


def save_listing(listing, timestamp):
    """
    Save listing dictionary into listing file.
    """
    listing_id = listing["UXSCore"]["mad_uxscoreid"]

    versions_dir_path = config.VERSIONS_DIR(listing_id)
    listing_file_path = config.LISTING_FILE(listing_id, timestamp)
    temporary_file_path = listing_file_path.with_suffix(".tmp")

    ensure_dir(versions_dir_path)

    with open(temporary_file_path, "w", encoding="utf-8") as file:
        json.dump(listing, file, indent=2)

    temporary_file_path.replace(listing_file_path)

    logger.debug(
        "Saved listing %s at %s",
        listing_id,
        timestamp,
    )


def load_stored_listing_ids():
    """
    Return all locally stored listing IDs.
    """
    active_listings_path = config.ACTIVE_LISTINGS_FILE

    ensure_file(active_listings_path, "{}")

    with open(active_listings_path, "r", encoding="utf-8") as file:
        stored_listing_ids = set(json.load(file))

    return stored_listing_ids


def save_active_listing_ids(listing_ids):
    """
    Save listing IDs of seen listings into active listings file.
    """
    active_listings_path = config.ACTIVE_LISTINGS_FILE
    temporary_file_path = active_listings_path.with_suffix(".tmp")

    with open(temporary_file_path, "w", encoding="utf-8") as file:
        json.dump(list(listing_ids), file)

    temporary_file_path.replace(active_listings_path)


def save_to_index(listing):
    """
    Save essential listing information into index file.
    """
    index_file_path = config.INDEX_FILE

    ensure_file(index_file_path)

    manufacturer = listing["manufacturer"]["mad_id"]
    product_type = listing["UXSCore"]["mad_coretype"]
    product_name = listing["UXSCore"]["mad_id"]
    listing_id = listing["UXSCore"]["mad_uxscoreid"]

    with open(index_file_path, "a", encoding="utf-8") as file:
        index_entry = {
            "manufacturer": manufacturer,
            "product_type": product_type,
            "product_name": product_name,
            "listing_id": listing_id,
        }
        file.write(json.dumps(index_entry) + "\n")

    logger.debug(
        "Indexed new listing %s | %s | %s at %s",
        manufacturer,
        product_type,
        product_name,
        listing_id,
    )


def blue_list_tracker():
    """
    Find blue list changes and return them.
    """
    results = []

    listings = get_listings()

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S.%fZ")

    seen_listing_ids = set()

    # Counts for logging
    new_count = 0
    updated_count = 0
    removed_count = 0
    reactivated_count = 0

    for listing in listings:
        result = {"old_listing": None, "new_listing": None}

        listing_id = listing["UXSCore"]["mad_uxscoreid"]
        listing_string = json.dumps(listing, sort_keys=True)
        listing_hash = sha256(listing_string.encode("utf-8")).hexdigest()

        seen_listing_ids.add(listing_id)

        metadata, existed = load_metadata(listing_id)

        # Listing has changed
        if not existed or listing_hash != metadata["listing_hash"]:
            # Newly seen listing
            if not existed:
                # Update index
                save_to_index(listing)

                # Update metadata
                metadata["first_seen"] = timestamp

                logger.info(
                    "New listing discovered: %s",
                    listing_id,
                )

                new_count += 1
            # Updated listing
            else:
                # Update result
                result["old_listing"] = load_listing(listing_id)

                logger.info(
                    "Listing updated: %s",
                    listing_id,
                )

                updated_count += 1
            # Save listing
            save_listing(listing, timestamp)

            # Update metadata
            metadata["is_active"] = True
            metadata["last_updated"] = timestamp
            metadata["listing_id"] = listing_id
            metadata["listing_hash"] = listing_hash

            # Update result
            result["new_listing"] = listing

            # Update results
            results.append(result)
        # An inactive listing becomes active again
        elif metadata["is_active"] is False:
            # Update metadata
            metadata["is_active"] = True

            # Update result
            result["new_listing"] = listing
            result["old_listing"] = listing

            # Update results
            results.append(result)

            logger.info(
                "Listing reactivated: %s",
                listing_id,
            )

            reactivated_count += 1
        # Update metadata
        metadata["last_seen"] = timestamp

        # Save metadata
        save_metadata(metadata, listing_id)

    logger.debug(
        "Seen %d active listings",
        len(seen_listing_ids),
    )

    stored_listing_ids = load_stored_listing_ids()

    logger.debug(
        "Found %d stored listings",
        len(stored_listing_ids),
    )

    save_active_listing_ids(seen_listing_ids)

    removed_listing_ids = stored_listing_ids - seen_listing_ids

    # Listings no longer shown
    for listing_id in removed_listing_ids:
        result = {"old_listing": None, "new_listing": None}

        # Get local listing
        listing = load_listing(listing_id)

        # Update metadata
        metadata, _ = load_metadata(listing_id)
        metadata["is_active"] = False

        # Save metadata
        save_metadata(metadata, listing_id)

        # Update result
        result["old_listing"] = listing

        # Update results
        results.append(result)

        logger.info(
            "Listing removed: %s",
            listing_id,
        )

        removed_count += 1

    logger.info(
        "Changes: %d new, %d updated, %d removed, %d reactivated",
        new_count,
        updated_count,
        removed_count,
        reactivated_count,
    )

    return results


def run():
    """
    Execute the blue_list_tracker workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting blue_list_tracker")

    results = blue_list_tracker()

    logger.debug("Stopping blue_list_tracker")

    return results
