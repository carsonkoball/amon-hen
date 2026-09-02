import logging

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging
from amon_hen.common.tracker import Tracker

# Logging setup
logger = logging.getLogger(__name__)


def _get_solution_ids():
    """
    Initiate GET request for DIU solutions catalog and return the listed solution slugs.
    """
    logger.debug("Fetching DIU solution IDs...")

    solution_ids = []

    response = http_get(url=config.SOLUTIONS_URL)

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    solutions = soup.find_all(class_="table")[1:]

    for solution in solutions:
        solution_id = solution.find("a")["href"].split("/")[-1]

        solution_ids.append(solution_id)

    logger.debug("Retrieved %d solution IDs", len(solution_ids))

    return solution_ids


def _process_solution(solution_id):
    """
    Retrieve relevant solution information.
    """
    logger.debug("Fetching solution %s...", solution_id)

    result = {}

    response = http_get(url=config.SOLUTION_URL(solution_id=solution_id))

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    title = list(soup.find("h1").stripped_strings)

    result["company_partner"] = title[0].rstrip(" —")
    result["project"] = title[1]
    
    aside_info = soup.find("aside").find_all("p")

    if len(aside_info) == 4:
        result["diu_focus_area"] = aside_info[1].text
        result["year_completed"] = aside_info[0].text
    else:
        result["diu_focus_area"] = aside_info[0].text
        result["year_completed"] = None

    description = soup.find_all(class_="richtext")

    result["problem"] = description[0].find("p").text
    result["solution"] = description[1].find("p").text
        
    return result


def _log_results(results):
    """
    Log the results of the tracking process.
    """
    if not results:
        logger.info("no solution changes found")
    if results:
        for result in results:
            if result.is_new:
                status = "added"
            elif result.is_removed:
                status = "removed"
            else:
                status = "modified"

            logger.info(
                "%s solution %s %s | company_partner: %s project: %s year_completed: %s",
                result.label["diu_focus_area"],
                result.identifier,
                status,
                result.label["company_partner"],
                result.label["project"],
                result.label["year_completed"],
            )


def _diu_solution_tracker(tracker):
    """
    Find DIU solutions changes and return them.
    """
    records = {}

    solution_ids = _get_solution_ids()

    # Process solutions
    for solution_id in solution_ids:
        solution = _process_solution(solution_id)

        label = {
            "company_partner": solution["company_partner"],
            "project": solution["project"],
            "year_completed": solution["year_completed"],
            "diu_focus_area": solution["diu_focus_area"],
        }

        records[solution_id] = {"label": label, "data": solution}

    results = tracker.track(records=records, path=config.SOLUTIONS_DIR)

    _log_results(results)

    return results


def run():
    """
    Execute the diu_solution_tracker workflow.
    """
    # Setup logging
    setup_logging()

    tracker = Tracker()

    logger.debug("Starting diu_solution_tracker")

    results = _diu_solution_tracker(tracker=tracker)

    logger.debug("Stopping diu_solution_tracker")

    return results
