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

# Base URL
SEARCH_URL = "https://www.war.gov/News/Contracts/StartDate/{start_date_year}-{start_date_month}-{start_date_day}/EndDate/{end_date_year}-{end_date_month}-{end_date_day}/?Page={page}"

# Base headers
SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Phrases that indicate an award is being received
AWARD_PHRASES = [
    "are awarded",
    "are being awarded",
    "are each being awarded",
    "are each awarded",
    "are modified in",
    "are receiving modifications",
    "are sharing",
    "being awarded",
    "has been awarded",
    "have been awarded",
    "have each been awarded",
    "is awarded",
    "is being awarded",
    "was awarded",
    "was competitively awarded",
    "were awarded",
    "were each awarded",
    "will be awarded",
    "will compete",
    "will each be awarded",
]

# Phrases that indicate an award is being updated
UPDATE_PHRASES = [
    "are being modified",
    "has been added as an awardee",
    "have each been added as an awardee",
]

# Contract award code patterns
# X: Any character
# A: Alphabetic character
# 0: Numberic character
# -: Dash
AWARD_CODES = [
    # AA0000-00--A0000
    r"[A-Z]{2}\d{4}-\d{2}--[A-Z]\d4}",
    # XXXXXXXXXXXXXA00000
    r"[A-Z0-9]{13}[A-Z]\d{5}",
    # XXXXXX-XX-X-XXXX
    r"[A-Z0-9]{6}-[A-Z0-9]{2}-[A-Z0-9]-[A-Z0-9]{4}",
    # AA000000A000
    r"[A-Z]{2}\d{6}[A-Z]\d{3}",
    # AXX00000AX000(/A00000)?
    r"[A-Z][A-Z0-9]{2}\d{5}[A-Z][A-Z0-9]\d{3}(/[A-Z]\d{5})?",
    # A00000-00A-X000
    r"[A-Z]\d{5}-\d{2}[A-Z]-[A-Z0-9]\d{3}",
    # A0000000-A-X000
    r"[A-Z]\d{7}-[A-Z]-[A-Z0-9]\d{3}",
]

# Patterns for award sections
AWARD_PATTERNS = [
    (r"^(?!correction:)", r",*\s*" + "(?:" + "|".join(AWARD_PHRASES) + ")"),
    # https://www.war.gov/News/Contracts/Contract/Article/4483936/contracts-for-may-12-2026/
    (r"is awarding a.*?contract.*?to.*?companies: ", r". Technical"),
    # https://www.war.gov/News/Contracts/Contract/Article/4364107/contracts-for-dec-18-2025/
    (r"has awarded a.*?contract.*?to ", r". This"),
]

# Patterns for correction sections
CORRECTION_PATTERNS = [
    (
        r".*?(?:contract|modification|delivery order).*?announced.*?on.*?(?:for |to )",
        r"(?:,? for|, was| under solicitation)",
    ),
    # https://www.war.gov/News/Contracts/Contract/Article/4588178/contracts-for-sept-1-2026/
    (
        r".*?contract.*?announced.*?on.*?for ",
        r", for",
    ),
    (r".*?contract.*?awarded.*?to ", r"(?:(,)? on|, for|, incorrectly)"),
    # https://www.war.gov/News/Contracts/Contract/Article/4406926/contracts-for-feb-13-2026/
    (
        r"^",
        r", contract announced on",
    ),
]

# Patterns for update sections
UPDATE_PATTERNS = [
    (
        # r"^(?:update:)?\s*",
        r"^update:\s*",
        r",*\s*" + "(?:" + "|".join(UPDATE_PHRASES) + ")",
    )
]

# Combined section patterns
SECTION_PATTERNS = {
    "award": AWARD_PATTERNS,
    "correction": CORRECTION_PATTERNS,
    "update": UPDATE_PATTERNS,
}
