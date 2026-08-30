from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

CSO_DIR = DATA_DIR / "cso"
CCAO_DIR = DATA_DIR / "ccao"

# URLs
LISTINGS_URL = "https://www.diu.mil/work-with-us/open-solicitations"
PATHWAY_URL = "https://www.diu.mil/work-with-us/submit-solution/{pathway_id}"
