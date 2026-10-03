import copy
from dataclasses import dataclass, asdict
from datetime import date, datetime
import logging
import re

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.filesystem import setup_environment
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class Notice:
    notice_link: str
    transaction_number: int
    date: datetime
    acquiring_party: str
    acquired_party: str
    acquired_entities: list

    @property
    def as_dict(self) -> dict:
        return asdict(self)


def _process_notice(notice):
    """
    Parse information from each notice found in the FTC ETN database.
    """
    notice_link = config.ETN_SEARCH_URL.split("/legal-library")[0] + notice["about"]

    transaction_number = int(notice.find(class_="node-title").text.split(":")[0])

    date = datetime.fromisoformat(
        notice.select_one(".field--name-field-date time")["datetime"]
    )

    acquiring_party = notice.select_one(
        ".field--name-field-acquiring-party .field__item"
    ).text

    acquired_party = notice.select_one(
        ".field--name-field-acquired-party .field__item"
    ).text

    acquired_entities = [
        entity.text
        for entity in notice.select(".field--name-field-other-entities .field__item")
    ]

    result = Notice(
        notice_link=notice_link,
        transaction_number=transaction_number,
        date=date,
        acquiring_party=acquiring_party,
        acquired_party=acquired_party,
        acquired_entities=acquired_entities,
    )

    return result


def _get_search(start_date, end_date):
    """
    Initiate an ETN search using a given search date range.
    """
    start_date_string = start_date.strftime("%m/%d/%Y")
    end_date_string = end_date.strftime("%m/%d/%Y")

    logger.debug(
        "Fetching ET notices using search dates between %s and %s...",
        start_date_string,
        end_date_string,
    )

    params = copy.deepcopy(config.ETN_SEARCH_PARAMS)

    # Search by date
    params["start_date"] = start_date_string
    params["end_date"] = end_date_string

    search_results = []
    page = 0

    # Continue iterating the search results until the end is reached
    while True:
        response = http_get(
            url=config.ETN_SEARCH_URL, params=params, headers=config.ETN_SEARCH_HEADERS
        )

        soup = BeautifulSoup(markup=response.text, features="html.parser")

        pager = soup.find(class_="pager")

        notices = soup.find_all(class_="node--type-early-termination-notice")

        search_results.extend(notices)

        # No more search results
        if not pager or not pager.find(class_="last"):
            break

        page += 1
        params["page"] = page

    return search_results


def _ftc_etn_parser(start_date, end_date):
    """
    Get the daily FCC ETN page and return the relevant information on it.
    """
    results = []

    notices = _get_search(start_date=start_date, end_date=end_date)

    # Parse every notice found in the search
    for notice in notices:
        result = _process_notice(notice)

        results.append(result)

    return results


def _validate_arguments(start_date, end_date):
    """
    Ensure that inputted arguments are of valid types, values, etc.
    """
    # start_date must either be datetime.date object or ISO string
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(end_date, str):
        start_date = date.fromisoformat(start_date)
    elif not isinstance(start_date, date):
        raise TypeError("start_date must be a datetime.date object or an ISO string.")

    # end_date must either be datetime.date object or ISO string
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)
    elif not isinstance(end_date, date):
        raise TypeError("end_date must be a datetime.date object or an ISO string.")

    # start_date can't be after end_date
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date.")

    return start_date, end_date


def _log_results(results):
    """
    Log the results of the parsing process.
    """
    if not results:
        logger.info("no notices found")

        return

    for result in results:
        logger.info(
            "%s notice %d | %s acquiring from %s | entities: %s",
            result.date.strftime("%Y-%m-%d"),
            result.transaction_number,
            result.acquiring_party,
            result.acquired_party,
            result.acquired_entities,
        )


def run(start_date=None, end_date=None):
    """
    Execute the ftc_etn_parser workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting ftc_etn_parser...")
    logger.debug("Argument start_date: %s", start_date)
    logger.debug("Argument end_date: %s", end_date)

    start_date, end_date = _validate_arguments(start_date=start_date, end_date=end_date)

    results = _ftc_etn_parser(start_date=start_date, end_date=end_date)

    _log_results(results)

    logger.debug("Stopping ftc_etn_parser")

    return results
