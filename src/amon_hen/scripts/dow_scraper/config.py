from pathlib import Path

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

LOG_FILE = LOG_DIR / "logs.log"

DIRS = {"BASE_DIR": BASE_DIR, "DATA_DIR": DATA_DIR, "LOG_DIR": LOG_DIR}

FILES = {"LOG_FILE": (LOG_FILE, "")}

# Base URL
SEARCH_URL = "https://www.war.gov/News/Contracts/?Search=\"Contracts+for+{month}+{day}%2c+{year}\""

# Base headers
SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Phrases that indicate multiple companies are contracted
PLURAL_PHRASES = [
    "are awarded",
    "are being awarded",
    "are sharing",
    "were awarded",
    "will each be awarded",
    "will compete",
]

# Phrases that indicate a single company is contracted
SINGULAR_PHRASES = [
    "has been added as an awardee",
    "has been awarded",
    "is awarded",
    "is being awarded",
    "was awarded",
]
