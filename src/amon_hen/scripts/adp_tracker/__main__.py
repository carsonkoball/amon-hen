import argparse

from .adp_tracker import run

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(
        description="Monitors the ADP Career Center for a user-specified company."
    )

    parser.add_argument(
        "--cid",
        type=str,
        required=True,
        help="ADP Career Center client ID.",
    )

    parser.add_argument(
        "--ccid",
        type=str,
        required=True,
        help="ADP Career Center career center ID.",
    )

    args = parser.parse_args()

    results = run(cid=args.cid, ccid=args.ccid)
