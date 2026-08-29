import argparse
from datetime import date

from . import config
from .dow_parser import run

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(
        description="Monitors the Department of War (DoW) daily contract announcements page."
    )

    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        required=False,
        default=config.DEFAULT_START_DATE,
        help="Search start date (YYYY-MM-DD).",
    )

    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        required=False,
        default=config.DEFAULT_END_DATE,
        help="Search end date (YYYY-MM-DD).",
    )

    args = parser.parse_args()

    results = run(start_date=args.start_date, end_date=args.end_date)
