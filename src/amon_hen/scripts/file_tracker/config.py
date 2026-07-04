from pathlib import Path

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

WEBSITE_DIR = lambda netloc_id: DATA_DIR / netloc_id
TRACKED_FILE_DIR = lambda netloc_id, url_hash: WEBSITE_DIR(netloc_id) / url_hash
VERSIONS_DIR = (
    lambda netloc_id, url_hash: TRACKED_FILE_DIR(netloc_id, url_hash) / "versions"
)

LOG_FILE = LOG_DIR / "logs.log"
INDEX_FILE = lambda netloc_id: WEBSITE_DIR(netloc_id) / "index.json"
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

DIRS = {"BASE_DIR": BASE_DIR, "DATA_DIR": DATA_DIR, "LOG_DIR": LOG_DIR}

FILES = {"LOG_FILE": LOG_FILE}
