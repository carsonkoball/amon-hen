from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

LISTING_DIR = lambda listing_id: DATA_DIR / listing_id

LISTINGS_HISTORY_FILE = DATA_DIR / "history.jsonl"
LISTINGS_ACTIVE_FILE = DATA_DIR / "active.json"

# URLs
LISTINGS_URL = "https://bluelist.appsplatformportals.us/getUXSClearedList/"


# Data
def HISTORY_ENTRY(timestamp, listing_id, listing_info, event):
    return {
        "timestamp": timestamp,
        "listing_id": listing_id,
        "listing_info": listing_info,
        "event": event,
    }
