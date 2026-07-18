from pathlib import Path

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

LOG_FILE = LOG_DIR / "logs.log"

LISTINGS_DIR = DATA_DIR / "listings"
ACTIVE_LISTINGS_FILE = LISTINGS_DIR / "active_listings.json"
INDEX_FILE = LISTINGS_DIR / "index.jsonl"
LISTING_DIR = lambda uxs_core_id: LISTINGS_DIR / uxs_core_id
METADATA_FILE = lambda uxs_core_id: LISTING_DIR(uxs_core_id) / "metadata.json"
VERSIONS_DIR = lambda uxs_core_id: LISTING_DIR(uxs_core_id) / "versions"
LISTING_FILE = (
    lambda uxs_core_id, timestamp: VERSIONS_DIR(uxs_core_id) / f"{timestamp}.json"
)

DIRS = {
    "BASE_DIR": BASE_DIR,
    "DATA_DIR": DATA_DIR,
    "LOG_DIR": LOG_DIR,
    "LISTINGS_DIR": LISTINGS_DIR,
}

FILES = {"LOG_FILE": (LOG_FILE, "")}

# Base URLs
LISTINGS_URL = "https://bluelist.appsplatformportals.us/getUXSClearedList/"
