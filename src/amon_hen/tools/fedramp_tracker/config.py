from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

LISTING_TYPE_DIR = lambda listing_type: DATA_DIR / listing_type

# Base URLs
FEDRAMP_URL = "https://www.fedramp.gov/marketplace/products/__data.json"

# Data
LISTING_TYPES = [
    "Products",
    "Agencies",
    "Assessors",
    "Advisors",
    #"AtoMapping",
    #"ReuseMapping",
]
