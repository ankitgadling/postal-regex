import argparse
from . import analytics


def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(description="Postal Regex command-line tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # The 'stats' command
    stats_parser = subparsers.add_parser(
        "stats", help="Display local validation statistics."
    )
    stats_parser.add_argument(
        "--reset", action="store_true", help="Reset all recorded statistics."
    )

    args = parser.parse_args()

    if args.command == "stats":
        if args.reset:
            analytics.reset_stats()
        else:
            analytics.show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
