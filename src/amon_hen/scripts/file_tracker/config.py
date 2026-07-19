from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

WEBSITE_DIR = lambda netloc_id: DATA_DIR / netloc_id
TRACKED_FILE_DIR = lambda netloc_id, url_hash: WEBSITE_DIR(netloc_id) / url_hash
VERSIONS_DIR = (
    lambda netloc_id, url_hash: TRACKED_FILE_DIR(netloc_id, url_hash) / "versions"
)

LOG_FILE = LOG_DIR / "logs.log"
INDEX_FILE = lambda netloc_id: WEBSITE_DIR(netloc_id) / "index.jsonl"
METADATA_FILE = (
    lambda netloc_id, url_hash: TRACKED_FILE_DIR(netloc_id, url_hash) / "metadata.json"
)
METADATA_HISTORY_FILE = (
    lambda netloc_id, url_hash: TRACKED_FILE_DIR(netloc_id, url_hash) / "metadata.jsonl"
)
CONTENT_FILE = (
    lambda netloc_id, url_hash, content_hash, extension: VERSIONS_DIR(
        netloc_id, url_hash
    )
    / f"{content_hash}{extension}"
)
