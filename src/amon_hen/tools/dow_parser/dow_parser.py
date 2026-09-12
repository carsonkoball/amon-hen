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
class Announcement:
    date: datetime
    branch: str
    announcement_type: str
    companies: list | None
    url: str
    footnotes: dict | None
    text: str

    @property
    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Company:
    name: str
    designation: str


def _get_daily_links(start_date, end_date):
    """
    Recover all contract announcement page links for a given search date range.
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
        if (
            soup.find(attrs={"aria-label": "Next"}) is None
            or soup.find(attrs={"aria-label": "Next"})["href"] == "#"
        ):
            break

        page += 1

    return links


def _extract_date(link):
    """
    Parse an inputted DoW announcement link to create a valid datetime object.
    """
    date_string = link.split("for-")[1].rstrip("/")
    month_string = date_string.split("-")[0][:3]
    date_string = month_string + "-" + date_string.split("-", maxsplit=1)[1]

    return datetime.strptime(date_string, "%b-%d-%Y")


def _process_companies(text, footnotes):
    """
    Retrieve relevant information from a string containing company names and other information.
    """
    company_names = text.split(";")

    companies = []

    for company_name in company_names:
        # Filter unnecessary information off of company string
        leading_filter = r"^\s*(:?for|and)\s*"
        code_filter = (
            r"[(\s,]*"
            + "(:?"
            + r".*?\)|".join(config.AWARD_CODES)
            + r".*?\)"
            + ")"
            + r"[)\s,]*"
        )
        trailing_filter = r"[\s,]*$"
        combined_filter = leading_filter + "|" + code_filter + "|" + trailing_filter

        filtered_company_name = re.sub(combined_filter, "", company_name)

        # Find the asterisks
        asterisks = re.search(r"\*+", filtered_company_name)
        asterisks = None if asterisks is None else asterisks.group()

        if asterisks is None or asterisks not in footnotes:
            designation = None
        else:
            designation = footnotes[asterisks]

        # Remove them
        sanitized_company_name = re.sub(r"\*+", "", filtered_company_name).strip()

        company = Company(
            name=sanitized_company_name,
            designation=designation,
        )

        companies.append(company)

    return companies


def _process_footnote_section(text, footnotes):
    """
    Retrieve relevant information from a DoW announcement footnote section of text.
    """
    for line in text.strip().splitlines():
        # Leading asterisks ignoring spaces and capture the second half
        match = re.match(r"^\s*(?:\*\s*)*(.*)", text)
        asterisk_count = match.group(0).count("*")
        designation = match.group(1).strip()

        footnotes["*" * asterisk_count] = designation

    return footnotes


def _get_paragraphs(link):
    """
    Get body paragraphs from a DoW daily announcement page.
    """
    response = http_get(url=link)

    if response is None or not response.ok:
        logger.error("Failed to fetch page: %s", link)

        return None

    data = response.text

    soup = BeautifulSoup(data, "html.parser")

    # Scan through every text section
    body = soup.find(class_="body")

    if body is None:
        logger.debug("Page has no content")

        return None

    paragraphs = body.find_all("p")

    return paragraphs


def _process_paragraphs(paragraphs):
    """
    Organize paragraphs by military branch and populate footnotes.
    """
    branch_sections, footnotes, branch = {}, {}, None

    # Group sections by branch
    for paragraph in paragraphs:
        text = paragraph.text.strip()

        if paragraph.has_attr("style"):
            branch = text
        else:
            for sub_text in text.split("\n"):
                # Footnote
                if sub_text.lstrip().startswith("*"):
                    footnotes = _process_footnote_section(
                        text=sub_text, footnotes=footnotes
                    )
                    pass
                # Section accidentally separated by newline (Ex: https://www.war.gov/News/Contracts/Contract/Article/4545450/contracts-for-july-14-2026/)
                elif sub_text[0].islower():
                    previous_sub_text = branch_sections[branch].pop()
                    branch_sections.setdefault(branch, []).append(
                        previous_sub_text + sub_text
                    )
                # Actual announcement
                else:
                    branch_sections.setdefault(branch, []).append(sub_text)

    return branch_sections, footnotes


def _process_branch_sections(branch_sections, footnotes, link):
    """
    Retrieve relevant information from each branch announcement.
    """
    announcements = []

    # Iterate through each branch
    for branch, section in branch_sections.items():
        # Iterate through each announcement
        for text in section:
            if not text.strip():
                logger.debug("Skipping blank text section...")

                continue

            announcement = Announcement(
                date=_extract_date(link=link),
                branch=branch,
                announcement_type="award",
                companies=[],
                url=link,
                footnotes=footnotes,
                text=text,
            )

            found = False

            # Identify the type of announcement based on stored patterns
            for announcement_type, patterns in config.SECTION_PATTERNS.items():
                if found:
                    break

                for prefix, suffix in patterns:
                    match = re.search(
                        pattern=prefix + r"\s*(.*?)\s*" + suffix,
                        string=announcement.text,
                        flags=re.IGNORECASE,
                    )

                    # Once a match is found, extract relevant information
                    if match:
                        announcement.companies = _process_companies(
                            text=match.group(1), footnotes=footnotes
                        )
                        announcement.announcement_type = announcement_type

                        found = True

                        logger.debug("Processed %s section", announcement_type)

                        break

            if not found:
                logger.debug("Processed unknown section")

            announcements.append(announcement)

    return announcements


def _dow_parser(start_date, end_date):
    """
    Get the daily announcement pages for a given search date range and return the announcements on them.
    """
    results = []

    daily_links = _get_daily_links(start_date=start_date, end_date=end_date)

    for link in daily_links:
        paragraphs = _get_paragraphs(link=link)

        branch_sections, footnotes = _process_paragraphs(paragraphs=paragraphs)

        result = _process_branch_sections(
            branch_sections=branch_sections, footnotes=footnotes, link=link
        )

        results.extend(result)

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
        logger.info("no announcements found")

        return

    for result in results:
        companies = [company.name for company in result.companies]
        logger.info(
            "%s %s %s announcement | companies: %s",
            result.date.strftime("%Y-%m-%d"),
            result.branch,
            result.announcement_type,
            companies,
        )


def run(start_date=None, end_date=None):
    """
    Execute the dow_parser workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting dow_parser...")
    logger.debug("Argument start_date: %s", start_date)
    logger.debug("Argument end_date: %s", end_date)

    start_date, end_date = _validate_arguments(start_date=start_date, end_date=end_date)

    results = _dow_parser(start_date=start_date, end_date=end_date)

    _log_results(results)

    logger.debug("Stopping dow_parser")

    return results
