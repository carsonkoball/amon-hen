from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

SOLUTIONS_DIR = DATA_DIR / "solutions"

# URLs
SOLUTIONS_URL = "https://www.diu.mil/solutions/portfolio/catalog"
SOLUTION_URL = lambda solution_id: SOLUTIONS_URL + "/" + solution_id
