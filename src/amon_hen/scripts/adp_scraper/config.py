from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

ARCHIVE_DIR = DATA_DIR / "archive"

ACTIVE_FILE = DATA_DIR / "active_jobs.json"
REMOVED_FILE = DATA_DIR / "removed_jobs.jsonl"

DIRS = {"ARCHIVE_DIR": ARCHIVE_DIR}

FILES = {"ACTIVE_FILE": (ACTIVE_FILE, "{}"), "REMOVED_FILE": (REMOVED_FILE, "")}

# Query settings
N_TOP = 999

# Base URLs
INDEX_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid={cid}&timeStamp={timestamp}&ccId={ccid}&lang=en_US&ccId={ccid}&locale=en_US&$top={n_top}"
JOB_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{job_url_id}?cid={cid}&timeStamp={timestamp}&ccId={ccid}&lang=en_US&ccId={ccid}&locale=en_US"
POSTING_URL_TEMPLATE = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid={cid}&ccId={ccid}&lang=en_US&jobId={job_id}"
