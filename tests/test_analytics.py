import json
from pathlib import Path
import sys

# Add src folder to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex import analytics

def test_record_validation_and_load_stats(monkeypatch):
    """
    Test that recording validations correctly creates and updates the stats file.
    """
    temp_stats_file = Path.home() / ".postalregex_stats_temp.json"
    monkeypatch.setattr(analytics, 'STATS_FILE', temp_stats_file)

    # Ensure the file doesn't exist initially
    if temp_stats_file.exists():
        temp_stats_file.unlink()

    analytics.record_validation("US", is_valid=True)
    
    with open(temp_stats_file, "r") as f:
        stats = json.load(f)
    
    assert stats["US"]["valid"] == 1
    assert stats["US"]["invalid"] == 0

    analytics.record_validation("US", is_valid=False)
    
    with open(temp_stats_file, "r") as f:
        stats = json.load(f)
        
    assert stats["US"]["valid"] == 1
    assert stats["US"]["invalid"] == 1

    analytics.record_validation("CA", is_valid=True)
    
    with open(temp_stats_file, "r") as f:
        stats = json.load(f)
        
    assert stats["CA"]["valid"] == 1
    assert "invalid" in stats["CA"] # an 'invalid' key should be created

    temp_stats_file.unlink()

def test_get_stats(monkeypatch):
    """
    Test that get_stats correctly reads and returns data.
    """
    temp_stats_file = Path.home() / ".postalregex_stats_temp.json"
    monkeypatch.setattr(analytics, 'STATS_FILE', temp_stats_file)

    # 1. Test when file doesn't exist
    if temp_stats_file.exists():
        temp_stats_file.unlink()
    assert analytics.get_stats() == {}

    dummy_data = {"US": {"valid": 5, "invalid": 1}}
    with open(temp_stats_file, "w") as f:
        json.dump(dummy_data, f)
    
    assert analytics.get_stats() == dummy_data
    
    temp_stats_file.unlink()

def test_reset_stats(monkeypatch):
    """
    Test that reset_stats correctly deletes the statistics file.
    """
    temp_stats_file = Path.home() / ".postalregex_stats_temp.json"
    monkeypatch.setattr(analytics, 'STATS_FILE', temp_stats_file)

    with open(temp_stats_file, "w") as f:
        json.dump({"US": {"valid": 1, "invalid": 0}}, f)
    
    assert temp_stats_file.exists()

    analytics.reset_stats()

    assert not temp_stats_file.exists()
