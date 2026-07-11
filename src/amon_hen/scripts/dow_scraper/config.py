from pathlib import Path

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

LOG_FILE = LOG_DIR / "logs.log"

DIRS = {"BASE_DIR": BASE_DIR, "DATA_DIR": DATA_DIR, "LOG_DIR": LOG_DIR}

FILES = {"LOG_FILE": (LOG_FILE, "")}

# Base URLs
INDEX_URL = "https://www.war.gov/News/Contracts/"

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
