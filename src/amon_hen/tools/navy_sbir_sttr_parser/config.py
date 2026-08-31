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
SBIR_URL = "https://www.navysbirsearch.com/"
SBIR_SEARCH_URL = SBIR_URL + "widgets/search/retrieval/results.jsp"
SBIR_LISTING_URL = (
    SBIR_URL + "widgets/hyperlinking/awarddetails.jsp?url=Doc%20URL&id={link_id}"
)

# Data
MAX_RESULTS = 5000

SBIR_PAYLOAD = {
    "start": "",
    "summary": "context",
    "sentences": "3",
    "characters": "300",
    "highlight": "summaryterms",
    "combine": "simple",
    "modQuery": "",
    "fieldFilter": "",
    "databasematch": "",
    "fieldcheckvalue": "",
    "qsDisplay": "",
    "sessionUserName": "",
    "useIQLRules": "true",
    "databases": [
        "Navy",
        "SuccessStories",
    ],
    "PHASE": "",
    "FIRM_DUNS": "",
    "FIRM_NAME": "",
    "FIRM_ZIP": "",
    "FIRM_STATE": "",
    "TOPIC_NUMBER": "",
    "TPOC": "",
    "AWARD_FISCAL_YEAR": "",
    "CONTRACT_NUMBER": "",
    "KEYWORDS": "",
    "maxResults": str(MAX_RESULTS),
    "sort": "Relevance+Sort_Date:reversealphabetical",
    "mUseAwardDate": "on",
    "mFromDateMonth": "",
    "mFromDateDay": "",
    "mFromDateYear": "",
    "mToDateMonth": "",
    "mToDateDay": "",
    "mToDateYear": "",
    "boolEXACT": "",
    "boolOR": "",
    "boolNOT": "",
    "_": "",
}
