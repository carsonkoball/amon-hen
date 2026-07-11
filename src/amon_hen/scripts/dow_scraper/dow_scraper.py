from datetime import date
import logging

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.filesystem import setup_environment
from amon_hen.common.http import http_get
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


def split_on_phrases(paragraph, phrases):
    """
    Split paragraph on the phrase closest to the start from inputted list of phrases.
    """
    min_index = len(paragraph)
    min_phrase = ""

    for phrase in phrases:
        index = paragraph.find(phrase)

        if index < min_index and index > -1:
            min_index = index
            min_phrase = phrase

    if min_phrase:
        return paragraph.split(min_phrase)

    return []


def get_daily_url(contract_date=None):
    """
    Find today's contract page URL if it exists.
    """

    # Use date from contract_date argument, otherwise use today's date
    if contract_date is None:
        contract_date = date.today()
    day = str(contract_date.day)
    month = contract_date.strftime("%B")
    year = str(contract_date.year)

    response = http_get(config.INDEX_URL)

    if response is None or not response.ok:
        logger.error("Failed to fetch page: %s", config.INDEX_URL)

        return None

    data = response.text

    try:
        logger.debug("Searching for %s %s, %s contract URL...", month, day, year)

        soup = BeautifulSoup(data, "html.parser")

        daily_url = soup.find("listing-titles-only")["article-url"]
        daily_url_components = daily_url.rstrip("/").split("-")
        daily_url_day = daily_url_components[-2]
        daily_url_month = daily_url_components[-3].capitalize()
        daily_url_year = daily_url_components[-1]

        # Today's contract URL found
        if daily_url_day == day and daily_url_month == month and daily_url_year == year:
            logger.debug(
                "%s %s, %s contract URL found: %s",
                daily_url_month,
                daily_url_day,
                daily_url_year,
                daily_url,
            )

            return daily_url
        # Today's contract URL not found
        logger.info("%s %s, %s contract URL not found.", month, day, year)

        return None
    # Some error ocurred while getting today's contract URL
    except Exception as e:
        logger.exception(
            "Error while attempting to find %s %s, %s contract URL: %s.",
            month,
            day,
            year,
            str(e),
        )
        return None


def get_companies(daily_url):
    """
    Identify companies listed on the daily contract page.
    """
    response = http_get(daily_url)

    if response is None or not response.ok:
        logger.error("Failed to fetch page: %s", daily_url)

        return {}

    data = response.text

    soup = BeautifulSoup(data, "html.parser")

    # Ensure response contains valid HTML body
    body = soup.find(class_="body")

    if body is None:
        logger.error("Malformed daily contract page.")

        return {}

    companies = {}

    branch = ""

    # Scan through every text section
    for i, p in enumerate(body.find_all("p")):
        # Footnote
        if p.text.startswith("*"):
            logger.debug("Footnote in p %s.", str(i + 1))

            continue
        # Military branch
        if p.has_attr("style"):
            logger.debug("Military branch in p %s.", str(i + 1))

            branch = p.text
            companies[p.text] = []

            continue
        # Correction
        if p.text[:11] == "CORRECTION:":
            logger.debug("Correction in p %s.", str(i + 1))

            companies[branch].append(["corr" + p.text.split(". ")[0]])

            continue
        # Update
        if p.text[:7] == "UPDATE:":
            logger.debug("Update in p %s.", str(i + 1))

            companies[branch].append([p.text.split(". ")[0]])

            continue
        # Multiple companies
        split = split_on_phrases(p.text, config.PLURAL_PHRASES)
        if split:
            logger.debug("Multiple companies in p %s.", str(i + 1))

            multi = []
            for winner in split[0].split(";"):
                company = winner.split("(")[0]
                company = company.lstrip().rstrip()
                if company[:4] == "and ":
                    company = company[4:]

                multi.append(company)

            companies[branch].append(multi)

            continue
        # Single company
        split = split_on_phrases(p.text, config.SINGULAR_PHRASES)
        if split:
            logger.debug("Single company in p %s.", str(i + 1))

            winner = split[0]
            winner = winner.lstrip().rstrip()
            winner = winner.rstrip(",")
            companies[branch].append([winner])

            continue

        # Something not picked up
        logger.debug("Unclassified content in p %s.", str(i + 1))

        companies[branch].append(["ERROR in p " + str(i + 1)])

    return companies


def dow_scraper(contract_date=None):
    """
    Get the daily contract page and return the companies on it.
    """
    results = {"daily_url": None, "companies": None}

    daily_url = get_daily_url(contract_date)

    if daily_url is None:
        return results

    companies = get_companies(daily_url)

    # Log the companies
    logger.info("%d branches found.", len(companies))

    for branch in companies:
        logger.info("%s:", branch)
        for winner in companies[branch]:
            for company in winner:
                logger.info("    %s", company)

    results["daily_url"] = daily_url
    results["companies"] = companies

    return results


def run(contract_date=None):
    """
    Execute the dow_scraper workflow.
    """
    # Setup logging
    setup_logging()

    # Ensure environment is correctly setup
    setup_environment(directories=config.DIRS, files=config.FILES)

    logger.debug("Starting dow_scraper")
    logger.debug("Argument contract_date: %s", contract_date)

    results = dow_scraper(contract_date)

    logger.debug("Stopping dow_scraper")

    return results
