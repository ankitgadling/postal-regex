import json
import jsonschema
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "postal_codes.json"
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "data" / "schema.json"

def test_json_schema():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=data, schema=schema)
