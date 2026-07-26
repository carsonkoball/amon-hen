import argparse
from datetime import date

from . import config
from .fcc_els_parser import run


def main():
    # CLI arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Monitors the Federal Communications Commission (FCC) Experimental Licensing System (ELS).",
    )

    parser.add_argument(
        "--search-date",
        type=date.fromisoformat,
        required=False,
        default=config.DEFAULT_SEARCH_DATE,
        help="Search date (YYYY-MM-DD).",
    )

    args = parser.parse_args()

    run(search_date=args.search_date)


if __name__ == "__main__":
    main()
