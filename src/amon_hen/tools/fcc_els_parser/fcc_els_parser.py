import copy
from dataclasses import dataclass, asdict
from datetime import date
import logging

from bs4 import BeautifulSoup

from . import config
from amon_hen.common.http import http_get, http_post
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class Synopsis:
    current_form_link: str | None
    exhibits_link: str | None
    notes_link: str | None
    grant_link: str | None
    file_number: str
    applicant_name: str
    receipt_date: str
    status: str
    status_date: str
    application_data: dict | None

    @property
    def get_code(self) -> str:
        return self.file_number.split("-")[2]

    @property
    def get_type(self) -> str:
        return config.APPLICATION_CODE_MAP[self.get_code]

    @property
    def as_dict(self) -> dict:
        return asdict(self)


def _process_conventional_form(form, code):
    """
    Retrieve relevant information from the Conventional Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    if code == "CM" or code == "ML":
        result["Modification For"] = (
            soup.find(title="Modification For")
            .find(class_="small-content")
            .text.strip()
        )

    if code == "CN" or code == "CM" or code == "PL" or code == "ML":
        result["Estimated Duration"] = " ".join(
            soup.find(title="Estimated Duration")
            .find(class_="small-content")
            .text.strip()
            .split()
        )

        manufacturers = []
        manufacturer_entries = (
            soup.find(title="Manufacturer").find("table").find_all(recursive=False)[2:]
        )

        for manufacturer_entry in manufacturer_entries:
            entry = manufacturer_entry.find_all(recursive=False)

            manufacturer = {
                "Manufacturer Name": entry[0].text.strip(),
                "Model Number": entry[1].text.strip(),
                "No. of Units": entry[2].text.strip(),
                "Experimental": entry[3].text.strip(),
            }

            manufacturers.append(manufacturer)

        result["Manufacturer"] = manufacturers

        stations = []

        if soup.find(title="Station Location"):
            station_entries = soup.find(title="Station Location").find_all("tr")
            
            for station_entry in station_entries:
                entry = station_entry.find_all("td")

                if entry and entry[0].text.strip() == "0":
                    station = {
                        "City": entry[1].text.strip(),
                        "State": entry[2].text.strip(),
                        "Mobile": entry[5].text.strip(),
                    }
                    
                    stations.append(station)

        result["Station Location"] = stations
    else:
        renewal_entry = soup.find(title="Renewal Info").find_all(class_="small-content")

        renewal_information = {
            "File Number": renewal_entry[0].text.strip(),
            "Date Issued": renewal_entry[1].text.strip(),
            "Location": renewal_entry[3].text.strip(),
        }

        result["Renewal Information"] = renewal_information
        result["Changes Made"] = (
            soup.find(title="Changes Made").find(class_="small-content").text.strip()
        )

    return result


def _process_program_form(form):
    """
    Retrieve relevant information from the Process Program Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    clinical_trial_entry = (
        soup.find("label", attrs={"for": "hospital"})
        .parent.parent.find_all("td")[1]
        .text.strip()
    )
    result["Involving Clinical Testing Trials"] = (
        True if clinical_trial_entry == "YES" else False
    )

    result["Narrative Comment"] = (
        soup.find("label", attrs={"for": "comment_text"})
        .parent.parent.find_all("td")[1]
        .text.strip()
    )

    result["Location Information"] = {
        "State": soup.find("label", attrs={"for": "state"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
        "City": soup.find("label", attrs={"for": "city"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
    }

    return result


def _process_medical_testing_form(form):
    """
    Retrieve relevant information from the Medical Testing Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    result["Narrative Comment"] = (
        soup.find("label", attrs={"for": "comment_text"})
        .parent.parent.find_all("td")[1]
        .text.strip()
    )

    result["Location Information"] = {
        "State": soup.find("label", attrs={"for": "state"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
        "City": soup.find("label", attrs={"for": "city"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
    }

    return result


def _process_compliance_testing_form(form):
    """
    Retrieve relevant information from the Compliance Testing Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    result["Narrative Comment"] = (
        soup.find("label", attrs={"for": "comment_text"})
        .parent.parent.find_all("td")[1]
        .text.strip()
    )

    result["Location Information"] = {
        "State": soup.find("label", attrs={"for": "state"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
        "City": soup.find("label", attrs={"for": "city"})
        .parent.parent.find_all("td")[1]
        .text.strip(),
    }

    return result


def _process_sta_form(form):
    """
    Retrieve relevant information from the Special Temporary Authority Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    result["Explanation"] = (
        soup.find(title="Why Necessary").find(class_="small-content").text.strip()
    )
    result["Purpose of Operation"] = (
        soup.find(title="Purpose of Operation")
        .find(class_="small-content")
        .text.strip()
    )
    result["Operation Start Date"] = (
        soup.find(title="Location").find_all(class_="small-content")[0].text.strip()
    )
    result["Operation End Date"] = (
        soup.find(title="Location").find_all(class_="small-content")[1].text.strip()
    )

    manufacturers = []
    manufacturer_entries = (
        soup.find(title="Manufacturer").find("table").find_all(recursive=False)[2:]
    )

    for manufacturer_entry in manufacturer_entries:
        entry = manufacturer_entry.find_all(recursive=False)

        manufacturer = {
            "Manufacturer Name": entry[0].text.strip(),
            "Model Number": entry[1].text.strip(),
            "No. of Units": entry[2].text.strip(),
            "Experimental": entry[3].text.strip(),
        }

        manufacturers.append(manufacturer)

    result["Manufacturer"] = manufacturers

    stations = []

    if soup.find(title="Station Location"):
        station_entries = soup.find(title="Station Location").find_all("tr")
        
        for station_entry in station_entries:
            entry = station_entry.find_all("td")

            if entry and entry[0].text.strip() == "0":
                station = {
                    "City": entry[1].text.strip(),
                    "State": entry[2].text.strip(),
                    "Mobile": entry[5].text.strip(),
                }
                
                stations.append(station)

    result["Station Location"] = stations

    return result


def _process_administrative_action_form(form, code):
    """
    Retrieve relevant information from the Assignment of License or Transfer of Control Form type.
    """
    soup = BeautifulSoup(markup=form, features="html.parser")

    result = {}

    license_entries = soup.find(id="offTblBdy").find_all("tr")
    licenses = []

    for _license in license_entries:
        entry = {
            "Filing": config.ELS_URL + _license.find("td").find("a")["href"],
            "File Number": _license.find_all("td")[2].text.strip(),
            "Licensee Name" if code == "AU" else "Transferee Name": _license.find_all("td")[3].text.strip(),
        }

        licenses.append(entry)
        
    result["Assignments" if code == "AU" else "Transfers"] = licenses

    return result
    
def _process_legacy_form(form, code):
    """
    Retrieve relevant information from Legacy form types.
    """
    result = result = _process_conventional_form(form=form, code=code)
            
    return result


def _get_form(form_link):
    """
    Initiate GET request for specified form link and return response as text.
    """
    response = http_get(form_link)

    if response is None or not response.ok:
        logger.error("Failed to fetch form page: %s", form_link)

        return None

    logger.debug("Form page %s found", form_link)

    return response.text


def _parse_search(data):
    """
    Parse information from each listing found on the ELS table.
    """
    soup = BeautifulSoup(markup=data, features="html.parser")

    listings = soup.find(attrs={"name": "rsTable"})

    if listings is None:
        return []

    listings = listings.find("tbody")
    listings = listings.find_all("tr", recursive=False)

    search_results = []

    # Gather information from each row in the ELS table
    for listing in listings:
        values = listing.find_all("td")

        result = Synopsis(
            current_form_link=(
                config.ELS_URL + values[1].find_all("a")[1]["href"]
                if values[1].text.strip() != "Not Available"
                else None
            ),
            exhibits_link=(
                config.ELS_URL + values[2].find("a")["href"]
                if values[2].text.strip() != "N/A"
                else None
            ),
            notes_link=(
                config.ELS_URL + values[3].find("a")["href"].lstrip("javascript:openWindow('").rstrip("')")
                if values[3].text.strip() != "N/A"
                else None
            ),
            grant_link=(
                config.ELS_URL + values[5].find("a")["href"].lstrip("javascript:openWindow('").rstrip("')")
                if values[5].text.strip() != "N/A"
                else None
            ),
            file_number=values[6].text.strip(),
            applicant_name=values[8].text.strip(),
            receipt_date=values[9].text.strip(),
            status=values[10].text.strip(),
            status_date=values[11].text.strip(),
            application_data=None,
        )

        search_results.append(result)

    return search_results


def _get_search(search_date):
    """
    Initiate an ELS search using a given receipt date.
    """
    logger.debug(
        "Fetching ELS applications using %s receipt date...",
        search_date.strftime("%m/%d/%Y"),
    )

    search_date_string = search_date.strftime("%m/%d/%Y")

    payload = copy.deepcopy(config.ELS_PAYLOAD)

    # Search by receipt date
    payload["receipt_date_from"] = search_date_string
    payload["receipt_date_to"] = search_date_string

    response = http_post(
        config.ELS_SEARCH_URL,
        data=payload,
    )

    return response.text


def _fcc_els_parser(search_date):
    """
    Get the daily ELS page and return relevant information on it.
    """
    data = _get_search(search_date=search_date)

    results = _parse_search(data=data)

    # Parse every application listing found in the search
    for result in results:
        listing_code = result.get_code
        listing_form_link = result.current_form_link
        current_form = _get_form(listing_form_link) if listing_form_link else None

        logger.debug(
            "Processing %s form (Number %s)...", result.get_type, result.file_number
        )

        # Different application types have different information that needs to be parsed separately
        if current_form:
            match listing_code:
                case "CN" | "CM" | "CR":
                    processed_form = _process_conventional_form(
                        form=current_form, code=listing_code
                    )
                case "PN" | "PM" | "PR":
                    processed_form = _process_program_form(form=current_form)
                case "MN" | "MM" | "MR":
                    processed_form = _process_medical_testing_form(form=current_form)
                case "TN" | "TM" | "TR":
                    processed_form = _process_compliance_testing_form(form=current_form)
                case "AU" | "TU":
                    processed_form = _process_administrative_action_form(form=current_form, code=listing_code)
                case "ST":
                    processed_form = _process_sta_form(form=current_form)
                case "PL" | "ML" | "RR":
                    processed_form = _process_legacy_form(form=current_form, code=listing_code)

            logger.debug(
                "Processed %s form (Number %s)", result.get_type, result.file_number
            )
        else:
            processed_form = None

        result.application_data = processed_form

    # Log the found applications
    logger.info("%d applications found for %s.", len(results), search_date)

    for result in results:
        logger.info(
            "Type: %s Applicant Name: %s File Number: %s",
            result.get_type,
            result.applicant_name,
            result.file_number,
        )

    return results


def run(search_date):
    """
    Execute the fcc_els_parser workflow.
    """
    # Setup logging
    setup_logging()

    logger.debug("Starting fcc_els_parser")
    logger.debug("Argument search_date: %s", search_date)

    results = _fcc_els_parser(search_date)

    logger.debug("Stopping fcc_els_parser")

    return results
