import sys
from pathlib import Path
import pytest
import subprocess
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


from postal_regex.bulk import (
    bulk_validate,
    bulk_normalize,
    validate_dataframe,
    validate_spark_dataframe,
    load_json,
    load_pandas,
    load_spark,
    export_csv,
    export_parquet,
)

# ----------------- Test Data -----------------
POSTAL_CODES = ["90210", "75001", "10115", "ABCDE"]
COUNTRIES = ["US", "FR", "DE", "FR"]


# ----------------- Helpers -----------------
def is_java_available():
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def is_spark_available():
    try:
        import pyspark

        return True
    except ImportError:
        return False


# ----------------- Bulk Function Tests -----------------
@pytest.mark.parametrize(
    "countries,expected",
    [
        (["US", "FR", "DE", "FR"], ["US", "FR", "DE", "FR"]),
        ([], []),  # empty input
        ([None, "FR"], [None, "FR"]),  # handle None
    ],
)
def test_bulk_normalize(countries, expected):
    assert bulk_normalize(countries) == expected


def test_bulk_validate_edge_cases():
    # Empty list
    assert bulk_validate("FR", []) == []

    # All invalid postal codes
    codes = ["XYZ", "123"]
    assert bulk_validate("FR", codes) == [False, False]

    # Mixed valid/invalid
    codes = ["75001", "XYZ", None]
    results = bulk_validate("FR", codes)
    assert results == [True, False, False]

    # Generator output type check
    gen_results = list(bulk_validate("FR", codes, as_generator=True))
    for code, valid in gen_results:
        assert isinstance(code, str) or code is None
        assert isinstance(valid, bool)


# ----------------- Pandas DataFrame Tests -----------------
def test_validate_dataframe_edge_cases():
    df = pd.DataFrame(
        {
            "country": ["FR", "DE", None],  # missing country allowed
            "postal_code": ["75001", "10115", np.nan],  # missing postal code
        }
    )

    # Fill NaN postal codes with None for safety
    df["postal_code"] = df["postal_code"].where(pd.notna(df["postal_code"]), None)

    df_validated = validate_dataframe(
        df, country_col="country", postal_col="postal_code"
    )

    # Validity checks
    assert df_validated["is_valid"].tolist() == [True, True, False]

    # Normalized countries
    assert df_validated["country_norm"].tolist() == ["FR", "DE", None]


# ----------------- Spark DataFrame Tests -----------------
@pytest.mark.optional
def test_validate_spark_dataframe_edge_cases():
    if not (is_spark_available() and is_java_available()):
        pytest.skip("Skipping Spark test: PySpark or Java not available")

    from pyspark.sql import SparkSession
    from pyspark.sql import Row

    spark = SparkSession.builder.master("local[1]").appName("TestPostal").getOrCreate()
    data = [
        Row(country="FR", postal_code="75001"),
        Row(country="DE", postal_code="10115"),
        Row(country=None, postal_code=None),
    ]
    df = spark.createDataFrame(data)
    df_validated = validate_spark_dataframe(
        df, country_col="country", postal_col="postal_code"
    )

    rows = df_validated.collect()
    assert [row["is_valid"] for row in rows] == [True, True, False]
    assert [row["country_norm"] for row in rows] == ["FR", "DE", None]

    spark.stop()


# ----------------- bulk load Tests -----------------
def test_load_json():
    data = load_json()
    assert isinstance(data, list)
    assert "country_code" in data[0]
    assert "postal_code_regex" in data[0]


def test_load_pandas():
    df = load_pandas()
    assert not df.empty
    assert "country_code" in df.columns
    assert "postal_code_regex" in df.columns


def test_export_parquet(tmp_path: Path):
    parquet_file = tmp_path / "postal_codes.parquet"
    out = export_parquet(parquet_file)
    assert out.exists()

    df = pd.read_parquet(out)
    assert not df.empty
    assert "country_code" in df.columns


@pytest.mark.optional
def test_load_spark(tmp_path: Path):
    if not (is_spark_available() and is_java_available()):
        pytest.skip("Skipping Spark test: PySpark or Java not available")

    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[1]").appName("TestPostalbulk").getOrCreate()
    )
    sdf = load_spark(spark)

    assert "country_code" in sdf.columns
    assert "postal_code_regex" in sdf.columns
    assert sdf.count() > 0

    spark.stop()
