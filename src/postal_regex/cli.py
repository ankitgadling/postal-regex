import argparse
import sys
from . import analytics
from .core import validate
from .errors import PostalRegexError, CountryNotSupportedError


def main():
    """
    Main function for the command-line interface.

    Handles command-line arguments and routes to appropriate functions.
    Provides user-friendly error messages for custom exceptions.

    Raises:
        SystemExit: Exits with code 1 on validation errors, 0 on success.
    """
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
        try:
            for code in args.postal_codes:
                is_valid = validate(args.country, code)
                result = "Valid" if is_valid else "Invalid"
                print(f"{code}: {result}")
        except CountryNotSupportedError as e:
            print(f"Error: {e}", file=sys.stderr)
            print(
                f"\nCountry '{e.country_identifier}' is not supported.",
                file=sys.stderr,
            )
            print("Use 'postal-regex --help' for more information.", file=sys.stderr)
            sys.exit(1)
        except PostalRegexError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
