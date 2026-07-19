from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

LISTINGS_DIR = DATA_DIR / "listings"
ACTIVE_LISTINGS_FILE = LISTINGS_DIR / "active_listings.json"
INDEX_FILE = LISTINGS_DIR / "index.jsonl"
LISTING_DIR = lambda uxs_core_id: LISTINGS_DIR / uxs_core_id
METADATA_FILE = lambda uxs_core_id: LISTING_DIR(uxs_core_id) / "metadata.json"
VERSIONS_DIR = lambda uxs_core_id: LISTING_DIR(uxs_core_id) / "versions"
LISTING_FILE = (
    lambda uxs_core_id, timestamp: VERSIONS_DIR(uxs_core_id) / f"{timestamp}.json"
)

DIRS = {"LISTINGS_DIR": LISTINGS_DIR}

# Base URLs
LISTINGS_URL = "https://bluelist.appsplatformportals.us/getUXSClearedList/"
