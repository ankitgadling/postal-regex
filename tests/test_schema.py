import json
import jsonschema
from pathlib import Path

# Paths relative to src/postal_regex/data
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "src" / "postal_regex" / "data" / "postal_codes.json"
SCHEMA_FILE = PROJECT_ROOT / "src" / "postal_regex" / "data" / "schema.json"


def test_json_schema():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Validate JSON data against the schema
    jsonschema.validate(instance=data, schema=schema)
