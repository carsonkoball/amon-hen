from datetime import datetime
from hashlib import sha256
import json
import logging
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, urlsplit, urlunsplit

from bs4 import BeautifulSoup
import requests

from . import config
from amon_hen.common import config_crawler
from amon_hen.common.crawler import Crawler
from amon_hen.common.filesystem import ensure_dir, ensure_file, setup_environment
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


class FileCrawler(Crawler):
    """
    Extend the base Crawler class to process and track files.
    """

    def __init__(self, exhaustive_search=True, allowed_extensions=None):
        """
        Initialize a FileCrawler with the specified search behavior and allowed file extensions.
        """
        super().__init__()

        self.allowed_extensions = set()
        self.allowed_extension_mimes = set()
        self.EXHAUSTIVE_SEARCH = exhaustive_search
        self.results = []

        self.set_allowed_extensions(allowed_extensions or set())

    def set_allowed_extensions(self, allowed_extensions):
        """
        Update list of extensions to search for.
        """
        self.allowed_extensions = set(allowed_extensions)
        self.allowed_extension_mimes = {
            config_crawler.EXTENSION_INFO[extension]["mime"]
            for extension in allowed_extensions
        }

    def _non_exhaustive_discard(self, parsed_link):
        """
        Determine whether an inputted parsed link should be considered for crawling.
        """
        # Exhaustive search keeps all links
        if self.EXHAUSTIVE_SEARCH:
            return False

        path = parsed_link.path.lower()
        suffix = PurePosixPath(path).suffix.lower()

        # No extension
        if not suffix:
            return False

        # Check against user selection of allowed extensions
        if self.allowed_extensions:
            return suffix not in self.allowed_extensions

        return True

    def _normalize_url(self, url):
        """
        Normalize an inputted url for consistency.
        """
        url_parts = urlsplit(url)
        normalized_url = urlunsplit(
            (
                url_parts.scheme.lower(),  # Keep scheme
                url_parts.netloc.lower(),  # Keep netloc
                url_parts.path or "",  # Keep path
                url_parts.query,  # Keep query
                "",  # Drop fragment
            )
        )

        return normalized_url

    def _extract_identity(self, response, content_type):
        """
        Retrieve information from inputted response for analysis.
        """
        normalized_url = self._normalize_url(response.url)
        parsed_url = urlparse(normalized_url)
        content = response.content
        extension = config_crawler.MIME_TO_EXTENSIONS[content_type][0]

        url_hash = sha256(normalized_url.encode("utf-8")).hexdigest()
        netloc_id = parsed_url.netloc
        content_hash = sha256(content).hexdigest()

        identity = {
            "normalized_url": normalized_url,
            "parsed_url": parsed_url,
            "content": content,
            "extension": extension,
            "url_hash": url_hash,
            "netloc_id": netloc_id,
            "content_hash": content_hash,
        }

        return identity

    def _ensure_environment(self, identity):
        """
        Validate the existence of relevant directories and files.
        """
        # Create directories if they don't already exist
        ensure_dir(config.WEBSITE_DIR(identity["netloc_id"]))
        ensure_dir(config.TRACKED_FILE_DIR(identity["netloc_id"], identity["url_hash"]))
        ensure_dir(config.VERSIONS_DIR(identity["netloc_id"], identity["url_hash"]))

        # Create files if they don't already exist
        ensure_file(config.INDEX_FILE(identity["netloc_id"]))
        ensure_file(
            config.METADATA_FILE(identity["netloc_id"], identity["url_hash"]), "{}"
        )
        ensure_file(
            config.METADATA_HISTORY_FILE(identity["netloc_id"], identity["url_hash"])
        )
        ensure_file(
            config.CONTENT_FILE(
                identity["netloc_id"],
                identity["url_hash"],
                identity["content_hash"],
                identity["extension"],
            )
        )

    def _load_metadata(self, identity):
        """
        Retrieve metadata from last file record.
        """
        metadata = {"content_hash": None}

        with open(config.METADATA_FILE(identity["netloc_id"], identity["url_hash"]), "r", encoding="utf-8") as file:
            metadata = json.load(file)
                
        metadata.setdefault("content_hash", None)

        return metadata

    def _process_response(self, response):
        """
        Process a downloaded response by:
        - Determining whether it represents a tracked file
        - Detecting content changes
        - Updating metadata and archiving new versions
        """
        result = {"old_file": None, "new_file": None}

        content_type = response.headers.get("Content-Type", "").split(";")[0]

        if content_type not in self.allowed_extension_mimes:
            return

        # Identity information
        identity = self._extract_identity(response, content_type)

        # Environment setup
        self._ensure_environment(identity)

        # Previous state
        metadata = self._load_metadata(identity)

        timestamp = datetime.now().isoformat()

        # File content has changed
        if identity["content_hash"] != metadata["content_hash"]:
            # Change is due to initial version of file being recorded
            if metadata["content_hash"] is None:
                # Update index file with url and url_hash key-value pair
                with open(
                    config.INDEX_FILE(identity["netloc_id"]), "a", encoding="utf-8"
                ) as file:
                    index_entry = {identity["normalized_url"]: identity["url_hash"]}
                    file.write(json.dumps(index_entry) + "\n")
            # Change is due to file update from previous version
            else:
                # Update result
                result["old_file"] = config.CONTENT_FILE(
                    identity["netloc_id"],
                    identity["url_hash"],
                    metadata["content_hash"],
                    metadata["extension"],
                )
                # Update metadata history file with previous metadata information
                with open(
                    config.METADATA_HISTORY_FILE(
                        identity["netloc_id"], identity["url_hash"]
                    ),
                    "a",
                    encoding="utf-8",
                ) as file:
                    file.write(json.dumps(metadata) + "\n")

            # Update results
            result["new_file"] = config.CONTENT_FILE(
                identity["netloc_id"],
                identity["url_hash"],
                identity["content_hash"],
                identity["extension"],
            )

            # Update metadata
            metadata["content_hash"] = identity["content_hash"]
            metadata["extension"] = identity["extension"]
            metadata["first_seen"] = timestamp

            # Update content file
            with open(
                config.CONTENT_FILE(
                    identity["netloc_id"],
                    identity["url_hash"],
                    identity["content_hash"],
                    identity["extension"],
                ),
                "wb",
            ) as file:
                file.write(identity["content"])

        # Update metadata
        metadata["last_checked"] = timestamp
        metadata["last_status"] = response.status_code

        # Update metadata file
        with open(
            config.METADATA_FILE(identity["netloc_id"], identity["url_hash"]), "w"
        ) as file:
            json.dump(metadata, file)

        if result["old_file"] or result["new_file"]:
            self.results.append(result)

    def crawl(self, *args, **kwargs):
        """
        Extend the base crawl method to manage results from crawling process.
        """
        self.results = []
        super().crawl(*args, **kwargs)
        return self.results


def file_tracker():
    """
    Find file changes and return them.
    """

    crawler = FileCrawler(exhaustive_search=False, allowed_extensions={".png"})
    results = crawler.crawl(base_url="https://www.castellumus.com/", max_depth=1)

    return results


def run():
    """
    Execute the file_tracker workflow.
    """
    # Setup logging
    setup_logging()

    # Ensure environment is correctly setup
    setup_environment(directories=config.DIRS, files=config.FILES)

    logger.debug("Starting file_scraper")

    results = file_tracker()

    logger.debug("Stopping file_scraper")

    return results
