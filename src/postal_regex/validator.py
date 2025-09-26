import json
import re
from functools import lru_cache


# Access postal_codes.json inside the installed package
from importlib.resources import files

DATA_FILE = files("postal_regex.data") / "postal_codes.json"

with DATA_FILE.open("r", encoding="utf-8") as f:
    _raw_data = json.load(f)

BY_CODE = {}
BY_NAME = {}

for entry in _raw_data:
    compiled = re.compile(entry["postal_code_regex"])
    record = {
        "country_code": entry["country_code"],
        "country_name": entry["country_name"],
        "regex": compiled,
    }
    BY_CODE[entry["country_code"].upper()] = record
    BY_NAME[entry["country_name"].upper()] = record


@lru_cache(maxsize=None)
def normalize(identifier: str) -> str:
    identifier = identifier.strip().upper()
    entry = BY_CODE.get(identifier) or BY_NAME.get(identifier)
    if not entry:
        raise ValueError(f"No match found for '{identifier}'")
    return entry["country_code"]


@lru_cache(maxsize=None)
def validate(country_identifier: str, postal_code: str) -> bool:
    identifier = country_identifier.strip().upper()
    entry = BY_CODE.get(identifier) or BY_NAME.get(identifier)
    if not entry:
        raise ValueError(f"No regex found for '{country_identifier}'")
    return bool(entry["regex"].match(postal_code))


def get_supported_countries():
    return [
        {"code": v["country_code"], "name": v["country_name"]} for v in BY_CODE.values()
    ]
