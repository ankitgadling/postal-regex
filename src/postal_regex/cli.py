import argparse
from . import analytics
from .core import validate


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

    # The 'validate' command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate postal codes for a given country."
    )
    validate_parser.add_argument(
        "postal_codes", nargs="+", help="Postal code(s) to validate."
    )
    validate_parser.add_argument(
        "country", help="Country code or name to validate against."
    )

    args = parser.parse_args()

    if args.command == "stats":
        if args.reset:
            analytics.reset_stats()
        else:
            analytics.show_stats()
    elif args.command == "validate":
        for code in args.postal_codes:
            is_valid = validate(args.country, code)
            result = "Valid" if is_valid else "Invalid"
            print(f"{code}: {result}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
