from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

CSO_DIR = DATA_DIR / "cso"
CCAO_DIR = DATA_DIR / "ccao"

CSO_PATHWAY_DIR = lambda pathway_id: CSO_DIR / pathway_id
CCAO_PATHWAY_DIR = lambda pathway_id: CCAO_DIR / pathway_id

CSO_HISTORY_FILE = CSO_DIR / "history.jsonl"
CSO_ACTIVE_FILE = CSO_DIR / "active.json"

CCAO_HISTORY_FILE = CCAO_DIR / "history.jsonl"
CCAO_ACTIVE_FILE = CCAO_DIR / "active.json"

# URLs
LISTINGS_URL = "https://www.diu.mil/work-with-us/open-solicitations"
PATHWAY_URL = "https://www.diu.mil/work-with-us/submit-solution/{pathway_id}"

# Data
def HISTORY_ENTRY(timestamp, pathway_id, pathway_info, event):
    return {
        "timestamp": timestamp,
        "pathway_id": pathway_id,
        "pathway_info": pathway_info,
        "event": event,
    }
