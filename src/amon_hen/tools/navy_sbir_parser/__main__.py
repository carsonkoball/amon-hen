import argparse
from datetime import date

from . import config
from .navy_sbir_parser import run


def main():
    # CLI arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Monitors the Navy Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) awards and success stories page.",
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

    # Start date can't be after end date
    if args.start_date > args.end_date:
        parser.error("--start-date must be on or before --end-date.")

    run(start_date=args.start_date, end_date=args.end_date)


if __name__ == "__main__":
    main()
