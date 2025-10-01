import pytest
import pandas as pd
import sys
from pathlib import Path
import json
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex.bulk import (
    bulk_validate,
    bulk_normalize,
    validate_dataframe,
    validate_spark_dataframe,
)

# ---------------------------
# Test Data
# ---------------------------
POSTAL_CODES = ["90210", "75001", "10115", "ABCDE"]
COUNTRIES = ["US", "FR", "DE", "FR"]

# ---------------------------
# Bulk Functions Tests
# ---------------------------
def test_bulk_normalize():
    normalized = bulk_normalize(COUNTRIES)
    assert normalized == ["US", "FR", "DE", "FR"]

def test_bulk_validate():
    # Validate against correct countries
    results = bulk_validate("FR", ["75001", "ABCDE"])
    assert results == [True, False]

def test_bulk_validate_generator():
    # Generator output
    gen = bulk_validate("FR", ["75001", "ABCDE"], as_generator=True)
    results = list(gen)
    assert results == [("75001", True), ("ABCDE", False)]

# ---------------------------
# Pandas DataFrame Test
# ---------------------------
def test_validate_dataframe_pandas():
    df = pd.DataFrame({
        "country": COUNTRIES,
        "postal_code": POSTAL_CODES
    })

    df_validated = validate_dataframe(df, country_col="country", postal_col="postal_code")
    expected = [True, True, True, False]
    assert df_validated["is_valid"].tolist() == expected
    # Ensure normalized countries are added
    assert df_validated["country_norm"].tolist() == ["US", "FR", "DE", "FR"]

# ---------------------------
# Spark DataFrame Test
# ---------------------------
def test_validate_spark_dataframe():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master("local[1]").appName("TestPostal").getOrCreate()
    data = list(zip(COUNTRIES, POSTAL_CODES))
    df = spark.createDataFrame(data, ["country", "postal_code"])

    df_validated = validate_spark_dataframe(df, country_col="country", postal_col="postal_code")
    result = [row["is_valid"] for row in df_validated.collect()]
    expected = [True, True, True, False]
    assert result == expected

    # Check normalized countries
    normalized = [row["country_norm"] for row in df_validated.collect()]
    assert normalized == ["US", "FR", "DE", "FR"]

    spark.stop()
