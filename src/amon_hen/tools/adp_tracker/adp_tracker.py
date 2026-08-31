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

        ensure_file(config.COMPANIES_INDEX_FILE)

        with open(config.COMPANIES_INDEX_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(obj=entry) + "\n")


def _log_results(results):
    """
    Log the results of the tracking process.
    """
    if not results:
        logger.info("no listing changes found")
    else:
        for result in results:
            if result.is_new:
                status = "added"
            elif result.is_removed:
                status = "removed"
            else:
                status = "modified"

            logger.info(
                "listing %s %s | title: %s",
                result.identifier,
                status,
                result.label["title"],
            )


def _adp_tracker(cid, ccid, tracker):
    """
    Find newly added and newly removed job postings and return them.
    """
    records = {}

    _initialize_company(cid=cid, ccid=ccid)

    postings_data = _get_postings(external_job_id=None, cid=cid, ccid=ccid)

    # Every listing found in current search
    for posting in postings_data["jobRequisitions"]:
        external_job_id = posting["customFieldGroup"]["stringFields"][0]["stringValue"]

        data = _get_postings(external_job_id=external_job_id, cid=cid, ccid=ccid)
        # Remove "CurrentServerDateTime" to prevent hash discrepancies on every scan
        del data["customFieldGroup"]["dateFields"][1]

        label = {"title": data["requisitionTitle"]}

        records[external_job_id] = {"label": label, "data": data}

    results = tracker.track(records=records, path=config.COMPANY_DIR(cid=cid))

    _log_results(results)

    return results


def run(cid, ccid):
    """
    Execute the adp_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting adp_tracker")
    logger.debug("Argument cid: %s", cid)
    logger.debug("Argument ccid: %s", ccid)

    results = _adp_tracker(cid=cid, ccid=ccid, tracker=tracker)

    logger.debug("Stopping adp_tracker")

    return results
