from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

COMPANY_DIR = lambda cid: DATA_DIR / cid

COMPANIES_INDEX_FILE = DATA_DIR / "index.jsonl"

# Query settings
N_TOP = 999

# Base URLs
POSTINGS_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid={cid}&timeStamp={timestamp}&ccId={ccid}&lang=en_US&ccId={ccid}&locale=en_US&$top={n_top}"
POSTING_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{external_job_id}?cid={cid}&timeStamp={timestamp}&ccId={ccid}&lang=en_US&ccId={ccid}&locale=en_US"
COMPANY_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/client-features?cid={cid}&timeStamp={timestamp}&ccId={ccid}&ccId={ccid}&lang=en_US"

# Argument settings
# xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CID_PATTERN = r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"

# 00000000_000000
CCID_PATTERN = r"^\d{8}_\d{6}$"
