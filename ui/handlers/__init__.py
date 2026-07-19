from . import adp_scraper
from . import blue_list_tracker
from . import dow_scraper
from . import file_tracker

HANDLERS = {
    "dow_scraper": dow_scraper,
    "blue_list_tracker": blue_list_tracker,
    "adp_scraper": adp_scraper,
    "file_tracker": file_tracker,
}
