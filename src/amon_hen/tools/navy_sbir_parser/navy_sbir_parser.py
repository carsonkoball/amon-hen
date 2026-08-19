import copy
from dataclasses import dataclass, asdict
from datetime import date, datetime
import logging
import re
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.http import http_get, http_post
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class Synopsis:
    firm: str
    contract_number: str
    topic_number: str
    syscom: str
    award_amount: float
    solicitation: str
    phase: int
    start_date: datetime
    end_date: datetime
    program: str
    proposal_no: str
    last_update: datetime
    source: str
    proposal_title: str
    keywords: list
    awards: dict | None
    success_stories: dict | None
    abstract: str
    benefit: str

    @property
    def as_dict(self) -> dict:
        return asdict(self)


def _process_listing(listing):
    soup = BeautifulSoup(markup=listing, features="html.parser")

    firm_info = soup.find(id="FirmContent").find("table")
    meta_info = soup.find_all(id="asMeta")[1].find("table")
    doc_info = soup.find(id="docContent")
    related_info = soup.find(id="asRelatedInformation")

    keywords = meta_info.find_all("tr")[5].find_all("td")[1].text.split(",")

    awards = related_info.find_all("a")
    award_links = [
        config.SBIR_LISTING_URL.format(link_id=_extract_link_id(award["href"]))
        for award in awards
    ]
    award_names = [award.text.strip() for award in awards]

    description = doc_info.find("span").text.strip()

    # Capture everything between ABSTRACT and BENEFIT
    abstracts = re.findall(
        r"(?<=ABSTRACT:)\s*(.*?)(?=\s*BENEFIT:)", description, re.DOTALL
    )

    # Capture everything between BENEFIT and ABSTRACT or end of string
    benefits = re.findall(
        r"(?<=BENEFIT:)\s*(.*?)(?=\s*ABSTRACT:|$)", description, re.DOTALL
    )

    # Remove empty sections
    abstracts = [abstract.strip() for abstract in abstracts if abstract.strip()]
    benefits = [benefit.strip() for benefit in benefits if benefit.strip()]

    result = Synopsis(
        firm=firm_info.find_all("tr")[0].find_all("td")[1].text.strip(),
        contract_number=meta_info.find_all("tr")[0].find_all("td")[1].text.strip(),
        topic_number=meta_info.find_all("tr")[0].find_all("td")[3].text.strip(),
        syscom=meta_info.find_all("tr")[0].find_all("td")[5].text.strip(),
        award_amount=float(meta_info.find_all("tr")[1].find_all("td")[1].text.strip()),
        solicitation=meta_info.find_all("tr")[1].find_all("td")[3].text.strip(),
        phase=len(meta_info.find_all("tr")[1].find_all("td")[5].text.strip()),
        start_date=datetime.strptime(
            meta_info.find_all("tr")[2].find_all("td")[1].text.split("-")[0].strip(),
            "%m/%d/%Y",
        ),
        end_date=datetime.strptime(
            meta_info.find_all("tr")[2].find_all("td")[1].text.split("-")[1].strip(),
            "%m/%d/%Y",
        ),
        program=meta_info.find_all("tr")[2].find_all("td")[3].text.strip(),
        proposal_no=meta_info.find_all("tr")[3].find_all("td")[1].text.strip(),
        last_update=datetime.strptime(
            meta_info.find_all("tr")[3].find_all("td")[3].text.strip(), "%m/%d/%Y"
        ),
        source=meta_info.find_all("tr")[3].find_all("td")[5].text.strip(),
        proposal_title=meta_info.find_all("tr")[4].find_all("td")[1].text.strip(),
        keywords=[keyword.strip() for keyword in keywords],
        awards=dict(zip(award_names, award_links)),
        success_stories={},
        abstract="\n".join(abstracts),
        benefit="\n".join(benefits),
    )

    return result


def _get_listing(listing_link):
    """
    Initiate GET request for specified form link and return response as text.
    """
    response = http_get(listing_link)

    if response is None or not response.ok:
        logger.error("Failed to fetch listng page: %s", listing_link)

        return None

    logger.debug("Listing page %s found", listing_link)

    return response.text


def _extract_link_id(link):
    link_id = parse_qs(urlparse(link).query)["id"][0]

    return link_id


def _get_listing_links(start_date, end_date, start_index):
    """
    Initiate an SBIR/STTR search using a given award start date and listing index start.
    """
    logger.debug(
        "Fetching SBIR/STTR awards and success stories from index %s to %s using award date from %s to %s...",
        str(start_index),
        str(start_index + config.MAX_RESULTS),
        start_date.strftime("%m/%d/%Y"),
        end_date.strftime("%m/%d/%Y"),
    )

    start_date_year = start_date.strftime("%m")
    start_date_month = start_date.strftime("%m")
    start_date_day = start_date.strftime("%m")

    end_date_year = end_date.strftime("%m")
    end_date_month = end_date.strftime("%m")
    end_date_day = end_date.strftime("%m")

    payload = copy.deepcopy(config.SBIR_PAYLOAD)

    payload["start"] = str(start_index)

    # Search by award start date
    payload["mFromDateYear"] = start_date_year
    payload["mToDateYear"] = start_date_year
    payload["mFromDateMonth"] = start_date_month
    payload["mToDateMonth"] = end_date_month
    payload["mFromDateDay"] = end_date_day
    payload["mToDateDay"] = end_date_day

    response = http_post(
        config.SBIR_SEARCH_URL,
        data=payload,
    )

    soup = BeautifulSoup(markup=response.text, features="html.parser")

    listings = soup.find("div", id="mainDiv").find("table").find_all("tr")
    links = []

    # Create links to each listing found
    for listing in listings[3:-1]:
        link_id = _extract_link_id(listing.find("a")["href"])
        links.append(config.SBIR_LISTING_URL.format(link_id=link_id))

    return links


def _navy_sbir_parser(start_date, end_date):
    """
    Get the daily SBIR/STTR awards and success stories and return relevant information on them.
    """
    results = []

    i = 0

    # Maximum number of listings from a search is 5000 - search in chunks of 5000
    while True:
        # All listing links from current search
        listing_links = _get_listing_links(
            start_date=start_date,
            end_date=end_date,
            start_index=1 + (i * config.MAX_RESULTS),
        )

        if listing_links:
            for listing_link in listing_links:
                listing = _get_listing(listing_link)
                result = _process_listing(listing)

                results.append(result)
        else:
            break

        i += 1

    return results


def _validate_arguments(start_date, end_date):
    """
    Ensure that inputted arguments are of valid types, values, etc.
    """
    # end_date must either be datetime.date object or ISO string
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)
    elif not isinstance(end_date, date):
        raise TypeError("end_date must be a datetime.date object or an ISO string.")

    # start_date must either be datetime.date object or ISO string
    if isinstance(end_date, str):
        start_date = date.fromisoformat(start_date)
    elif not isinstance(start_date, date):
        raise TypeError("start_date must be a datetime.date object or an ISO string.")

    # start_date can't be after end_date
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date.")

    return start_date, end_date


def run(start_date, end_date):
    """
    Execute the navy_sbir_parser workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting navy_sbir_parser")
    logger.debug("Argument start_date: %s", start_date)
    logger.debug("Argument end_date: %s", end_date)

    start_date, end_date = _validate_arguments(start_date=start_date, end_date=end_date)
    results = _navy_sbir_parser(start_date=start_date, end_date=end_date)

    logger.debug("Stopping navy_sbir_parser")

    return results
