from dataclasses import dataclass, asdict
from datetime import date, datetime
import logging

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.filesystem import setup_environment
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class Announcement:
    date: datetime
    branch: str
    announcement_type: str
    companies: list | None
    url: str
    text: str

    @property
    def as_dict(self) -> dict:
        return asdict(self)


def _split_on_phrases(text, phrases):
    """
    Split text on the phrase closest to the start from inputted list of phrases.
    """
    min_index = len(text)
    min_phrase = ""

    for phrase in phrases:
        index = text.find(phrase)

        if index < min_index and index > -1:
            min_index = index
            min_phrase = phrase

    if min_phrase:
        return text.split(min_phrase)

    return []


def _get_daily_links(start_date, end_date):
    """
    Recovera all contract announcement page links for a given search date range.
    """
    start_date_year = start_date.strftime("%Y")
    start_date_month = start_date.strftime("%m")
    start_date_day = start_date.strftime("%d")

    end_date_year = end_date.strftime("%Y")
    end_date_month = end_date.strftime("%m")
    end_date_day = end_date.strftime("%d")

    links = []
    page = 1

    # Continue iterating the page number until the last page is reached
    while True:
        search_url = config.SEARCH_URL.format(
            start_date_day=start_date_day,
            start_date_month=start_date_month,
            start_date_year=start_date_year,
            end_date_day=end_date_day,
            end_date_month=end_date_month,
            end_date_year=end_date_year,
            page=page,
        )

        response = http_get(url=search_url, headers=config.SEARCH_HEADERS)

        if response is None or not response.ok:
            logger.error("Failed to fetch page: %s", search_url)

            continue

        data = response.text

        soup = BeautifulSoup(data, "html.parser")

        for link in soup.find_all("listing-titles-only"):
            links.append(link["article-url"])

        # The "next" button doesn't lead to another page
        if soup.find(attrs={"aria-label": "Next"})["href"] == "#":
            break

        page += 1

    return links


def _process_section(text, branch):
    """
    Retrieve relevant information from a DoW announcement section of text.
    """
    branch = branch
    companies = []

    # Correction section
    if text.startswith("CORRECTION"):
        announcement_type = "correction"
    # Update Section
    elif text.startswith("UPDATE"):
        announcement_type = "update"
    # Award section
    else:
        # Single-Award
        split = _split_on_phrases(text=text, phrases=config.SINGULAR_PHRASES)
        if split:
            announcement_type = "single_award"

            company = split[0].strip().rstrip(",")
            companies.append(company)
        # Multi-Award
        else:
            split = _split_on_phrases(text=text, phrases=config.PLURAL_PHRASES)

            announcement_type = "multi_award"

            for c in split[0].split(";"):
                company = c.split("(")[0].strip().removeprefix("and ")

                companies.append(company)

    result = Announcement(
        date=None,
        branch=branch,
        announcement_type=announcement_type,
        companies=companies,
        url=None,
        text=text,
    )

    return result


def _extract_date(link):
    """
    Parse an inputted DoW announcement link to create a valid datetime object.
    """
    date_string = link.split("for-")[1].rstrip("/")
    month_string = date_string.split("-")[0][:3]
    date_string = month_string + "-" + date_string.split("-", maxsplit=1)[1]

    return datetime.strptime(date_string, "%b-%d-%Y")


def _dow_parser(start_date, end_date):
    """
    Get the daily contract pages for a given search date range and return the announcements on them.
    """
    results = []

    daily_links = _get_daily_links(start_date=start_date, end_date=end_date)

    for link in daily_links:
        response = http_get(url=link)

        if response is None or not response.ok:
            logger.error("Failed to fetch page: %s", link)

            continue

        data = response.text

        soup = BeautifulSoup(data, "html.parser")

        branch = None

        # Scan through every text section
        for i, p in enumerate(soup.find(class_="body").find_all("p")):
            if p.text.startswith("*"):
                logger.debug("Footnote in p %s.", str(i + 1))
            elif p.has_attr("style"):
                branch = p.text

                logger.debug("Military branch in p %s.", str(i + 1))
            else:
                result = _process_section(text=p.text, branch=branch)
                result.url = link
                result.date = _extract_date(link=link)

                results.append(result)

                match result.announcement_type:
                    case "correction":
                        logger.debug("Correction in p %s.", str(i + 1))
                    case "update":
                        logger.debug("Update in p %s.", str(i + 1))
                    case "single_award":
                        logger.debug("Single-Award in p %s.", str(i + 1))
                    case "multi_award":
                        logger.debug("Multi-Award in p %s.", str(i + 1))

        # Log the found announcements
        for result in results:
            if (
                result.announcement_type == "correction"
                or result.announcement_type == "update"
            ):
                logger.info(
                    "Date: %s Type: %s",
                    result.date.strftime("%Y-%m-%d"),
                    result.announcement_type,
                )
            else:
                logger.info(
                    "Date: %s Type: %s Companies: %s",
                    result.date.strftime("%Y-%m-%d"),
                    result.announcement_type,
                    result.companies,
                )

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


def run(start_date=None, end_date=None):
    """
    Execute the dow_parser workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting dow_parser")
    logger.debug("Argument start_date: %s", start_date)
    logger.debug("Argument end_date: %s", end_date)

    start_date, end_date = _validate_arguments(start_date=start_date, end_date=end_date)
    results = _dow_parser(start_date=start_date, end_date=end_date)

    logger.debug("Stopping dow_parser")

    return results
