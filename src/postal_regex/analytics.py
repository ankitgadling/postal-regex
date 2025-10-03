import json
from pathlib import Path

STATS_FILE = Path.home() / ".postalregex_stats.json"


def _load_stats():
    """Load statistics from the local JSON file."""
    if not STATS_FILE.exists():
        return {}
    with open(STATS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_stats(stats):
    """Save statistics to the local JSON file."""
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def record_validation(country_code, is_valid):
    """
    Record a validation attempt for a given country.

    Args:
        country_code (str): The ISO 3166-1 alpha-2 country code.
        is_valid (bool): True if the validation was successful, False otherwise.
    """
    stats = _load_stats()

    # Ensure the country entry exists
    if country_code not in stats:
        stats[country_code] = {"valid": 0, "invalid": 0}

    # Increment the appropriate counter
    if is_valid:
        stats[country_code]["valid"] += 1
    else:
        stats[country_code]["invalid"] += 1
    _save_stats(stats)


def reset_stats():
    """Clear all recorded statistics."""
    if STATS_FILE.exists():
        STATS_FILE.unlink()
        print("Local validation statistics have been reset.")
    else:
        print("No statistics file found to reset.")


def get_stats() -> dict:
    """
    Loads and returns the validation statistics from the stats file.
    This function only retrieves data and does not print anything.

    Returns:
        dict: A dictionary containing the validation stats,
        or an empty dict if none exist.
    """
    if not STATS_FILE.exists():
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def show_stats():
    """
    Loads and prints a formatted dashboard of the validation statistics.
    This function handles all presentation logic.
    """
    stats = get_stats()  # This is the main change: call the new data function
    if not stats:
        print("No validation statistics recorded yet.")
        return

    # Prepare data for the table
    table_data = []
    for country, counts in stats.items():
        valid = counts.get("valid", 0)
        invalid = counts.get("invalid", 0)
        total = valid + invalid
        table_data.append([country, valid, invalid, total])

    # Sort by total validations
    table_data.sort(key=lambda row: row[3], reverse=True)

    # --- Print Table ---
    print("\nPostal Code Validation Stats (Local Project)")
    header = ["Country", "Valid", "Invalid", "Total"]
    col_widths = [len(h) for h in header]
    for row in table_data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = " | ".join(h.ljust(w) for h, w in zip(header, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(separator)

    for row in table_data:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        print(row_line)

    # --- Print Bar Chart ---
    print("\nValidation Success Rate")
    for country, valid, invalid, total in table_data:
        if total == 0:
            success_rate = 0
        else:
            success_rate = (valid / total) * 100
        bar_length = 40
        filled_length = int(bar_length * success_rate / 100)
        bar = "█" * filled_length + " " * (bar_length - filled_length)
        print(f"{country.ljust(5)} |{bar}| {success_rate:.0f}% valid")
