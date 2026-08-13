from . import adp_tracker
from . import blue_list_tracker
from . import dow_parser
from . import fcc_els_parser

HANDLERS = {
    "adp_tracker": adp_tracker,
    "blue_list_tracker": blue_list_tracker,
    "dow_parser": dow_parser,
    "fcc_els_parser": fcc_els_parser,
}
