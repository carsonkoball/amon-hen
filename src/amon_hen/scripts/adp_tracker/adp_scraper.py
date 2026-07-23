from datetime import datetime, timezone
import json
import logging

from . import config
from amon_hen.common.filesystem import ensure_file
from amon_hen.common.http import safe_json, http_get
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging setup
logger = logging.getLogger(__name__)


def _get_postings(external_job_id, cid, ccid):
    """
    Initiate GET request for either a specified company's postings page or a specified job posting page and return the response in JSON format.
    """
    if external_job_id:
        url = config.POSTING_URL_TEMPLATE.format(
            cid=cid,
            ccid=ccid,
            external_job_id=external_job_id,
            timestamp=datetime.now(),
        )
    else:
        url = config.POSTINGS_URL_TEMPLATE.format(
            cid=cid,
            ccid=ccid,
            timestamp=datetime.now(),
            n_top=config.N_TOP,
        )

    response = http_get(url=url)

    data = safe_json(response=response)

    return data


def _append_to(entry, path):
    """
    Save an entry to an append-only JSONL file.
    """
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(obj=entry) + "\n")


def _load_active(cid):
    """
    Load IDs from the active.json file.
    """
    postings_active_path = config.POSTINGS_ACTIVE_FILE(cid=cid)
    ensure_file(path=postings_active_path, default_content="[]")

    with open(file=postings_active_path, mode="r", encoding="utf-8") as file:
        previous_active = set(json.load(file))

    return previous_active


def _save_active(current_active, cid):
    """
    Save IDs to the active.json file.
    """
    postings_active_path = config.POSTINGS_ACTIVE_FILE(cid=cid)

    with open(file=postings_active_path, mode="w", encoding="utf-8") as file:
        json.dump(obj=sorted(current_active), fp=file, indent=2)


def _initialize_company(cid, ccid):
    """
    Add company to company index if needed.
    """
    if not config.COMPANY_DIR(cid=cid).exists():
        url = config.COMPANY_URL_TEMPLATE.format(
            cid=cid, ccid=ccid, timestamp=datetime.now()
        )

        response = http_get(url=url)

        data = safe_json(response=response)

        company_name = data["meta"]["customFieldGroup"]["stringFields"][7][
            "stringValue"
        ]

        entry = {"cid": cid, "company_name": company_name}
        _append_to(entry=entry, path=config.COMPANIES_INDEX_FILE)


def _adp_scraper(cid, ccid, tracker):
    """
    Find newly added and newly removed job postings and return them.
    """
    results = []

    _initialize_company(cid=cid, ccid=ccid)

    postings_data = _get_postings(external_job_id=None, cid=cid, ccid=ccid)

    current_active = set()

    # Every listing found in current search
    for posting in postings_data["jobRequisitions"][:1]:
        external_job_id = posting["customFieldGroup"]["stringFields"][0]["stringValue"]

        current_active.add(external_job_id)

        data = _get_postings(external_job_id=external_job_id, cid=cid, ccid=ccid)

        # Remove "CurrentServerDateTime" to prevent hash discrepancies on every scan
        del data["customFieldGroup"]["dateFields"][1]

        posting_path = config.POSTING_DIR(cid=cid, external_job_id=external_job_id)

        result = tracker.track(data=data, path=posting_path)

        # Modified listing
        if result.has_changed:
            results.append(result)

            # New listing
            if result.is_new:
                # Mark as newly added in index
                postings_index_file_path = config.POSTINGS_INDEX_FILE(cid=cid)

                entry = {
                    "time": datetime.now(timezone.utc)
                    .isoformat(timespec="seconds")
                    .replace("+00:00", "Z"),
                    "external_job_id": external_job_id,
                    "requisition_title": result.new_data["requisitionTitle"],
                    "event": "added",
                }

                _append_to(entry=entry, path=postings_index_file_path)

    # Load previously active postings
    previous_active = _load_active(cid=cid)

    # Save current active postings
    _save_active(current_active=current_active, cid=cid)

    # Determine removed postings
    removed = previous_active - current_active

    # Every listing found to be removed
    for external_job_id in removed:
        posting_path = config.POSTING_DIR(cid=cid, external_job_id=external_job_id)

        result = tracker.track(data=None, path=posting_path)

        # Mark as removed in index
        postings_index_file_path = config.POSTINGS_INDEX_FILE(cid=cid)

        entry = {
            "time": datetime.now(tz=timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "external_job_id": external_job_id,
            "requisition_title": result.old_data["requisitionTitle"],
            "event": "removed",
        }

        _append_to(entry=entry, path=postings_index_file_path)

        results.append(result)

    return results


def run(cid, ccid):
    """
    Execute the adp_scraper workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting adp_scraper")
    logger.debug("Argument cid: %s", cid)
    logger.debug("Argument ccid: %s", ccid)

    results = _adp_scraper(cid=cid, ccid=ccid, tracker=tracker)

    logger.debug("Stopping adp_scraper")

    return results
