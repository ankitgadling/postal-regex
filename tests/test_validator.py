import sys
from pathlib import Path
import json
import pytest

# Add src folder to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex import validator

# Load JSON the same way validator.py does
DATA_FILE = SRC_DIR / "postal_regex" / "data" / "postal_codes.json"
with open(DATA_FILE, "r", encoding="utf-8") as f:
    POSTAL_CODES = json.load(f)

# ----------------- Tests -----------------


@pytest.mark.parametrize("entry", POSTAL_CODES)
def test_validate_samples(entry):
    code = entry["country_code"]
    name = entry["country_name"]

    assert validator.validate(code, entry["sample_valid"]) is True
    assert validator.validate(name, entry["sample_valid"]) is True
    assert validator.validate(code, entry["sample_invalid"]) is False
    assert validator.validate(name, entry["sample_invalid"]) is False


@pytest.mark.parametrize("entry", POSTAL_CODES)
def test_normalize(entry):
    code = entry["country_code"]
    name = entry["country_name"]

    assert validator.normalize(code) == code
    assert validator.normalize(name) == code


def test_invalid_country_raises():
    with pytest.raises(ValueError):
        validator.validate("XX", "12345")
    with pytest.raises(ValueError):
        validator.normalize("NotACountry")
