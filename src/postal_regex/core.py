import json
import regex  # safer regex engine with timeout support
from functools import lru_cache
from dataclasses import dataclass
from importlib.resources import files

# ---------------------------
# Data Loading
# ---------------------------
DATA_FILE = files("postal_regex.data") / "postal_codes.json"

with DATA_FILE.open("r", encoding="utf-8") as f:
    _raw_data = json.load(f)


@dataclass(frozen=True)
class CountryRecord:
    country_code: str
    country_name: str
    regex: regex.Pattern


# Build lookup tables
BY_CODE = {}
COUNTRY_INDEX = {}

for entry in _raw_data:
    compiled = regex.compile(entry["postal_code_regex"])
    record = CountryRecord(
        country_code=entry["country_code"],
        country_name=entry["country_name"],
        regex=compiled,
    )
    code = entry["country_code"].upper()
    name = entry["country_name"].upper()
    BY_CODE[code] = record
    COUNTRY_INDEX[code] = record
    COUNTRY_INDEX[name] = record


# ---------------------------
# Core Functions
# ---------------------------
@lru_cache(maxsize=None)
def normalize(identifier: str) -> str:
    """
    Normalize a country identifier (code or name) to its ISO 3166-1 alpha-2 code.
    """
    key = identifier.strip().upper()
    entry = COUNTRY_INDEX.get(key)
    if not entry:
        raise ValueError(f"No match found for '{identifier}'")
    return entry.country_code


def get_entry(identifier: str) -> CountryRecord:
    """
    Retrieve the CountryRecord for a given country identifier.
    """
    code = normalize(identifier)
    return BY_CODE[code]


@lru_cache(maxsize=None)
def validate(country_identifier: str, postal_code: str, timeout: float = 0.1) -> bool:
    """
    Validate a postal code against the regex pattern for a given country.
    Timeout (default 100ms) prevents ReDoS hangs.
    """
    entry = get_entry(country_identifier)
    try:
        return bool(entry.regex.fullmatch(postal_code, timeout=timeout))
    except regex.TimeoutError:
        return False

def get_supported_countries():
    """
    Retrieve supported countries for postal code validation.
    """
    return [
        {"code": rec.country_code, "name": rec.country_name} for rec in BY_CODE.values()
    ]


def get_country_regex(country_identifier: str) -> str:
    """
    Retrieve the postal code regex pattern for a given country.
    """
    entry = get_entry(country_identifier)
    return entry.regex.pattern
