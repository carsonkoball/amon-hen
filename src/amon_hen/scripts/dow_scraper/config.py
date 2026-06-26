from pathlib import Path

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

LOG_FILE = LOG_DIR / "logs.log"

DIRS = {"BASE_DIR": BASE_DIR, "DATA_DIR": DATA_DIR, "LOG_DIR": LOG_DIR}

FILES = {"LOG_FILE": LOG_FILE}

# Base URLs
INDEX_URL = "https://www.war.gov/News/Contracts/"
DAILY_URL = None

# Phrases that indicate multiple companies are contracted
PLURAL_PHRASES = [
    "are awarded",
    "were awarded",
    "are being awarded",
    "will compete",
    "will each be awarded",
]

# Phrases that indicate a single company is contracted
SINGULAR_PHRASES = [
    "has been awarded",
    "was awarded",
    "is awarded",
    "is being awarded",
    "has been added as an awardee",
]
