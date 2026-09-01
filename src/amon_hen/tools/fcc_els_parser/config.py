from datetime import date
from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

# Default Arguments
DEFAULT_START_DATE = date.today()
DEFAULT_END_DATE = date.today()

# URLs
ELS_URL = "https://apps.fcc.gov/"
ELS_SEARCH_URL = ELS_URL + "oetcf/els/reports/GenericSearchResult.cfm"

# Data
ELS_HEADERS = {"content-type": "application/x-www-form-urlencoded"}

MAX_RESULTS = 999999

ELS_PAYLOAD = {
    "id_file_num": "",
    "callsign": "",
    "FRN": "",
    "name_licensee": "",
    "purpose_of_operation": "",
    "narrative_comments": "",
    "grant_date_from": "",
    "grant_date_to": "",
    "receipt_date_from": "",
    "receipt_date_to": "",
    "expiration_date_from": "",
    "expiration_date_to": "",
    "lower_frequency": "",
    "upper_frequency": "",
    "frequency_type": "",
    "frequency_type_description": "",
    "erp_from": "",
    "erp_to": "",
    "power_type": "n",
    "power_type_description": "nW",
    "emission": "",
    "scope_of_service": "",
    "experiment_type": "   ",
    "experiment_type_description": "",
    "tx_city": "",
    "transmitter_state": "",
    "transmitter_state_description": "",
    "all": "Y",
    "assignment_of_license": "Y",
    "modification_of_license": "Y",
    "new_license": "Y",
    "renewal_license": "Y",
    "special_temporary_authority": "Y",
    "transfer_of_control": "Y",
    "program_license": "Y",
    "medical_license": "Y",
    "compliance_license": "Y",
    "conventional_license": "Y",
    "FromRec": "1",
    "show_records": str(MAX_RESULTS),
    "fetchfrom": "0",
}

APPLICATION_CODE_MAP = {
    # Conventional
    "CN": "Conventional New",
    "CM": "Conventional Modification",
    "CR": "Conventional Renewal",
    # Program
    "PN": "Program New",
    "PM": "Program Modification",
    "PR": "Program Renewal",
    # Medical Testing
    "MN": "Medical Testing New",
    "MM": "Medical Testing Modification",
    "MR": "Medical Testing Renewal",
    # Compliance Testing
    "TN": "Compliance Testing New",
    "TM": "Compliance Testing Modification",
    "TR": "Compliance Testing Renewal",
    # Administrative actions
    "AU": "Assignment of License",
    "TU": "Transfer of Control",
    # Special Temporary Authority
    "ST": "Special Temporary Authority",
    # Legacy
    "PL": "Legacy License New",
    "ML": "Legacy License Modification",
    "RR": "Legacy License Renewal",
}
