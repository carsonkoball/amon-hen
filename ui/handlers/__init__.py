from . import adp_tracker
from . import blue_list_tracker
from . import diu_pathway_tracker
from . import dow_parser
from . import fcc_els_parser
from . import navy_sbir_sttr_parser

HANDLERS = {
    "adp_tracker": adp_tracker,
    "blue_list_tracker": blue_list_tracker,
    "diu_pathway_tracker": diu_pathway_tracker,
    "dow_parser": dow_parser,
    "fcc_els_parser": fcc_els_parser,
    "navy_sbir_sttr_parser": navy_sbir_sttr_parser,
}
