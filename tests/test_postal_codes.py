import json
import re
from pathlib import Path
import pytest

# Path to the JSON file
DATA_FILE = Path(__file__).resolve().parent.parent / "src" / "postal_regex" / "data" / "postal_codes.json"

# Load JSON data
with open(DATA_FILE, "r", encoding="utf-8") as f:
    POSTAL_CODES = json.load(f)

def test_no_duplicate_country_code_or_name():
    """Ensure no duplicate country_code or country_name exists in the JSON."""
    seen_codes = set()
    seen_names = set()
    duplicate_codes = set()
    duplicate_names = set()
    
    for entry in POSTAL_CODES:
        code = entry.get("country_code")
        name = entry.get("country_name")
        
        if code in seen_codes:
            duplicate_codes.add(code)
        else:
            seen_codes.add(code)
        
        if name in seen_names:
            duplicate_names.add(name)
        else:
            seen_names.add(name)
    
    assert not duplicate_codes, f"Duplicate country codes found: {', '.join(duplicate_codes)}"
    assert not duplicate_names, f"Duplicate country names found: {', '.join(duplicate_names)}"

@pytest.mark.parametrize("entry", POSTAL_CODES)
def test_postal_code_regex(entry):
    """Check that postal_code_regex matches sample_valid and rejects sample_invalid."""
    regex = entry.get("postal_code_regex")
    sample_valid = entry.get("sample_valid")
    sample_invalid = entry.get("sample_invalid")
    
    pattern = re.compile(regex)
    
    assert pattern.fullmatch(sample_valid), (
        f"Valid postal code '{sample_valid}' did not match regex for {entry['country_name']}"
    )
    
    assert not pattern.fullmatch(sample_invalid), (
        f"Invalid postal code '{sample_invalid}' incorrectly matched regex for {entry['country_name']}"
    )
