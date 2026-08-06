import argparse

from .file_tracker import run

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(
        description="Searches websites for files with user-specified extensions (e.g. .pdf, .csv, .png)."
    )

    parser.add_argument(
        "--base_url",
        type=str,
        required=True,
        help="Base URL to search from.",
    )

    parser.add_argument(
        "--max_depth",
        type=int,
        required=False,
        default=1,
        help="Maximum number of link hops to take from base url. Defaults to 1.",
    )

    parser.add_argument(
        "--exhaustive_search",
        type=bool,
        required=False,
        default=True,
        help="Determines whether or not to search all found links. Defaults to True.",
    )

    parser.add_argument(
        "--allowed_extensions",
        type=str,
        nargs="+",
        required=False,
        default=list(),
        help="List of file extensions to archive. Defaults to an empty set.",
    )

    args = parser.parse_args()

    results = run(
        base_url=args.base_url,
        max_depth=args.max_depth,
        exhaustive_search=args.exhaustive_search,
        allowed_extensions=args.allowed_extensions,
    )
