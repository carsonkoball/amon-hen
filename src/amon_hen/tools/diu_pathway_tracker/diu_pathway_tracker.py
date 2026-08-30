from datetime import datetime, UTC
import json
import logging

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.filesystem import ensure_file
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging seup
logger = logging.getLogger(__name__)


def _append_to(entry, path):
    """
    Save an entry to an append-only JSONL file.
    """
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(obj=entry) + "\n")


def _save_active(current_cso_active, current_ccao_active):
    """
    Save IDs to the active.json file for each pathway type.
    """
    cso_active_file_path = config.CSO_ACTIVE_FILE
    ccao_active_file_path = config.CCAO_ACTIVE_FILE

    with open(file=cso_active_file_path, mode="w", encoding="utf-8") as file:
        json.dump(obj=sorted(current_cso_active), fp=file, indent=2)

    with open(file=ccao_active_file_path, mode="w", encoding="utf-8") as file:
        json.dump(obj=sorted(current_ccao_active), fp=file, indent=2)


def _load_active():
    """
    Load IDs from the active.json file for each pathway type.
    """
    cso_active_file_path = config.CSO_ACTIVE_FILE
    ccao_active_file_path = config.CCAO_ACTIVE_FILE

    ensure_file(path=cso_active_file_path, default_content="[]")
    ensure_file(path=ccao_active_file_path, default_content="[]")

    with open(file=cso_active_file_path, mode="r", encoding="utf-8") as file:
        previous_cso_active = set(json.load(file))

    with open(file=ccao_active_file_path, mode="r", encoding="utf-8") as file:
        previous_ccao_active = set(json.load(file))

    return previous_cso_active, previous_ccao_active


def _get_pathway_ids():
    """
    Initiate GET request for DIU pathway page and return the CSO and CCAO pathway IDs.
    """
    logger.debug("Fetching DIU pathway listings...")

    response = http_get(config.LISTINGS_URL)

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    # Find CSO Pathways
    cso_pathways = soup.find_all(class_="pathway")[3].find_all("a")
    cso_pathway_ids = [
        cso_pathway["href"].split("/")[-1] for cso_pathway in cso_pathways
    ]

    # Find CCAO Pathways
    ccao_pathways = soup.find_all(class_="pathway")[4].find_all("a")
    ccao_pathway_ids = [
        ccao_pathway["href"].split("/")[-1] for ccao_pathway in ccao_pathways
    ]

    logger.debug(
        "Retrieved %d CSO pathways and %d CCAO pathways",
        len(cso_pathway_ids),
        len(ccao_pathway_ids),
    )

    return cso_pathway_ids, ccao_pathway_ids


def _process_pathway(pathway_id, pathway_type):
    """
    Retrieve relevant pathway information.
    """
    logger.debug("Fetching %s pathway %s...", pathway_type, pathway_id)

    result = {}

    response = http_get(config.PATHWAY_URL.format(pathway_id=pathway_id))

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    result["id"] = pathway_id

    result["type"] = pathway_type

    result["title"] = soup.find("h1").text.strip()

    result["due_by"] = soup.find(class_="richtext").find("p").text.strip()

    result["description"] = soup.find(class_="info").prettify()

    return result


def _log_results(results, listing_type):
    """
    Log the results of the tracking process.
    """
    if results:
        for result in results:
            if result.is_new:
                logger.info(
                    "%s pathway %s added | title: %s",
                    result.label["type"],
                    result.identifier,
                    result.label["title"],
                )
            elif result.is_removed:
                logger.info(
                    "%s pathway %s removed | title: %s",
                    result.label["type"],
                    result.identifier,
                    result.label["title"],
                )
            else:
                logger.info(
                    "%s pathway %s modified | title: %s",
                    result.label["type"],
                    result.identifier,
                    result.label["title"],
                )
    else:
        logger.info("no %s pathway changes found", listing_type)


def _diu_pathway_tracker(tracker):
    """
    Find DIU pathway changes and return them.
    """
    cso_records, ccao_records = {}, {}

    cso_pathway_ids, ccao_pathway_ids = _get_pathway_ids()

    # Process CSO pathways
    for pathway_id in cso_pathway_ids:
        pathway = _process_pathway(pathway_id, "CSO")

        label = {"type": pathway["type"], "title": pathway["title"]}

        cso_records[pathway_id] = {"label": label, "data": pathway}    

    # Process CCAO pathways
    for pathway_id in ccao_pathway_ids:
        pathway = _process_pathway(pathway_id, "CCAO")

        label = {"type": pathway["type"], "title": pathway["title"]}

        cso_records[pathway_id] = {"label": label, "data": pathway}

    cso_results = tracker.track(records=ccao_records, path=config.CCAO_DIR)
    ccao_results = tracker.track(records=ccao_records, path=config.CCAO_DIR)

    _log_results(cso_results, "CSO")
    _log_results(ccao_results, "CCAO")

    return cso_results, ccao_results


def run():
    """
    Execute the blue_list_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting diu_pathway_tracker")

    cso_results, ccao_results = _diu_pathway_tracker(tracker=tracker)

    logger.debug("Stopping diu_pathway_tracker")

    return cso_results, ccao_results
