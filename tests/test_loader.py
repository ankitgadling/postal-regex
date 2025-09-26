import sys
from pathlib import Path
import pytest
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex import loader


# ----------------- Helper -----------------
def is_java_available():
    """Check if Java is installed and JAVA_HOME is set"""
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


# ----------------- Tests -----------------
def test_load_json():
    data = loader.load_json()
    assert isinstance(data, list)
    assert "country_code" in data[0]
    assert "postal_code_regex" in data[0]


def test_load_pandas():
    df = loader.load_pandas()
    assert not df.empty
    assert "country_code" in df.columns
    assert "postal_code_regex" in df.columns


def test_export_parquet(tmp_path: Path):
    parquet_file = tmp_path / "postal_codes.parquet"
    out = loader.export_parquet(parquet_file)

    assert out.exists()
    # Check if it's actually parquet by trying to load with pandas
    import pandas as pd

    df = pd.read_parquet(out)
    assert not df.empty
    assert "country_code" in df.columns


@pytest.mark.optional
def test_load_spark(tmp_path: Path):
    if not (is_spark_available() and is_java_available()):
        pytest.skip("Skipping Spark test: PySpark or Java not available")

    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[1]")
        .appName("TestPostalLoader")
        .getOrCreate()
    )
    sdf = loader.load_spark(spark)

    assert "country_code" in sdf.columns
    assert "postal_code_regex" in sdf.columns
    assert sdf.count() > 0

    spark.stop()
