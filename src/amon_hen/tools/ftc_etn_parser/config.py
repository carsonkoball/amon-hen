from datetime import date
from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

# Default Arguments
DEFAULT_START_DATE = date.today()
DEFAULT_END_DATE = date.today()

# URLs
ETN_SEARCH_URL = "https://www.ftc.gov/legal-library/browse/early-termination-notices"

# Data
MAX_RESULTS = 100

ETN_SEARCH_PARAMS = {
    "sort_by": "field_date",
    "items_per_page": str(MAX_RESULTS),
    "search": "",
    "field_competition_topics": "All",
    "field_consumer_protection_topics": "All",
    "field_federal_court": "All",
    "field_industry": "All",
    "field_case_status": "All",
    "field_enforcement_type": "All",
    "search_matter_number": "",
    "search_civil_action_number": "",
    "start_date": "",
    "end_date": "",
    "page": "",
}

ETN_SEARCH_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
}
