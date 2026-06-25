from pathlib import Path
import time

# Storage
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
ACTIVE_FILE = BASE_DIR / "data" / "active_jobs.json"
REMOVED_FILE = BASE_DIR / "data" / "removed_jobs.jsonl"

LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "logs.log"

ARCHIVE_DIR = BASE_DIR / "data" / "archive"

# Company ADP information
CID = "244ae70f-13c8-4ab6-b68a-c2964191a80a"
CCID = "19000101_000001"

# Query settings
N_TOP = 999
TIMESTAMP = time.time()

# Base URLs
INDEX_URL = f"https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid={CID}&timeStamp={TIMESTAMP}&ccId={CCID}&lang=en_US&ccId={CCID}&locale=en_US&$top={N_TOP}"
JOB_URL = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{job_url_id}?cid={cid}&timeStamp={timestamp}&ccId={ccid}&lang=en_US&ccId={ccid}&locale=en_US"
POSTING_URL = f"https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid={CID}&ccId={CCID}&lang=en_US&jobID="
