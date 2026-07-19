from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

# Base URL
SEARCH_URL = "https://www.war.gov/News/Contracts/StartDate/{year}-{month}-{day}/EndDate/{year}-{month}-{day}/"

# Base headers
SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Phrases that indicate multiple companies are contracted
PLURAL_PHRASES = [
    "are awarded",
    "are being awarded",
    "are sharing",
    "have been awarded",
    "have each been awarded",
    "were awarded",
    "will each be awarded",
    "will compete",
]

# Phrases that indicate a single company is contracted
SINGULAR_PHRASES = [
    "has been added as an awardee",
    "has been awarded",
    "is awarded",
    "is being awarded",
    "was awarded",
    "will be awarded",
]
