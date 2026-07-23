from . import adp_tracker
from . import blue_list_tracker
from . import dow_scraper
from . import file_tracker

HANDLERS = {
    "dow_scraper": dow_scraper,
    "blue_list_tracker": blue_list_tracker,
    "adp_tracker": adp_tracker,
    "file_tracker": file_tracker,
}
