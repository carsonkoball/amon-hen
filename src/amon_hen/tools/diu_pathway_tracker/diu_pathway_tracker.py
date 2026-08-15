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

    timestamp = datetime.now()

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

    return cso_pathway_ids, ccao_pathway_ids, timestamp


def _process_pathway(pathway_id, is_cso_pathway):
    """
    Retrieve relevant pathway information.
    """
    logger.debug("Fetching pathway %s...", pathway_id)

    result = {}

    timestamp = datetime.now()

    response = http_get(config.PATHWAY_URL.format(pathway_id=pathway_id))

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    result["id"] = pathway_id

    result["type"] = "CSO" if is_cso_pathway else "CCAO"

    result["title"] = soup.find("h1").text.strip()

    result["due_by"] = soup.find(class_="richtext").find("p").text.strip()

    result["description"] = soup.find(class_="info").prettify()

    return result, timestamp


def _diu_pathway_tracker(tracker):
    """
    Find DIU pathway changes and return them.
    """
    results = []

    cso_pathway_ids, ccao_pathway_ids, removed_timestamp = _get_pathway_ids()

    current_cso_active = set()
    current_ccao_active = set()

    # Process seen pathways
    for index, pathway_id in enumerate(cso_pathway_ids + ccao_pathway_ids):
        is_cso_pathway = index < len(cso_pathway_ids)

        (
            current_cso_active.add(pathway_id)
            if is_cso_pathway
            else current_ccao_active.add(pathway_id)
        )

        pathway_path = (
            config.CSO_PATHWAY_DIR(pathway_id)
            if is_cso_pathway
            else config.CCAO_PATHWAY_DIR(pathway_id)
        )

        pathway, timestamp = _process_pathway(pathway_id, is_cso_pathway)

        result = tracker.track(data=pathway, path=pathway_path)

        # Modified listing
        if result.has_changed and not result.is_removed:
            results.append(result)

            # New listing
            if result.is_new:
                # Mark as newly added in history
                entry = config.HISTORY_ENTRY(
                    timestamp=timestamp.strftime("%Y-%m-%dT%H-%M-%S.%fZ"),
                    pathway_id=pathway_id,
                    pathway_info={"title": result.new_data["title"]},
                    event="added",
                )

                _append_to(
                    entry=entry,
                    path=(
                        config.CSO_HISTORY_FILE
                        if is_cso_pathway
                        else config.CCAO_HISTORY_FILE
                    ),
                )

    # Load previously active pathways
    previous_cso_active, previous_ccao_active = _load_active()

    # Save current active pathways
    _save_active(
        current_cso_active=current_cso_active, current_ccao_active=current_ccao_active
    )

    # Determine removed pathways
    removed_cso = previous_cso_active - current_cso_active
    removed_ccao = previous_ccao_active - current_ccao_active

    for index, pathway_id in enumerate(list(removed_cso) + list(removed_ccao)):
        # Every pathway found to be removed
        is_cso_pathway = index < len(cso_pathway_ids)

        pathway_path = (
            config.CSO_PATHWAY_DIR(pathway_id)
            if is_cso_pathway
            else config.CCAO_PATHWAY_DIR(pathway_id)
        )

        result = tracker.track(data=None, path=pathway_path)

        # Mark as removed in history
        entry = config.HISTORY_ENTRY(
            timestamp=removed_timestamp.strftime("%Y-%m-%dT%H-%M-%S.%fZ"),
            pathway_id=pathway_id,
            pathway_info={"title": result.new_data["title"]},
            event="removed",
        )

        _append_to(
            entry=entry,
            path=(
                config.CSO_HISTORY_FILE if is_cso_pathway else config.CCAO_HISTORY_FILE
            ),
        )

        results.append(result)

    # Log the pathways
    for result in results:
        if result.is_new:
            logger.info(
                "%s pathway added: %s", result.new_data["type"], result.new_data["id"]
            )
        elif result.is_removed:
            logger.info(
                "%s pathway removed: %s", result.old_data["type"], result.old_data["id"]
            )
        else:
            logger.info(
                "%s pathway modified: %s",
                result.new_data["type"],
                result.new_data["id"],
            )

    return results


def run():
    """
    Execute the blue_list_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting diu_pathway_tracker")

    results = _diu_pathway_tracker(tracker=tracker)

    logger.debug("Stopping diu_pathway_tracker")

    return results
