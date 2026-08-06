import argparse
from datetime import date

from .dow_parser import run

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(
        description="Monitors the Department of War (DoW) daily contract announcements page."
    )

    parser.add_argument(
        "--date",
        type=lambda x: date.fromisoformat(x),
        required=False,
        help="Contract date (YYYY-MM-DD). Defaults to today.",
    )

    args = parser.parse_args()

    results = run(contract_date=args.date)
