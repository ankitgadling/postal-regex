import sys
from pathlib import Path
import subprocess
import pytest

# ----------------- Project path setup -----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex import loader


# ----------------- Helpers -----------------
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


# ----------------- Benchmarks -----------------
@pytest.mark.benchmark
def test_validate_speed(benchmark):
    """Benchmark validate() on all sample valid codes"""
    data = loader.load_json()
    from postal_regex import validator

    def run_validation():
        for entry in data:
            validator.validate(entry["country_code"], entry["sample_valid"])

    benchmark(run_validation)


@pytest.mark.benchmark
def test_load_json_speed(benchmark):
    """Benchmark loading postal codes from JSON"""
    benchmark(loader.load_json)


@pytest.mark.benchmark
def test_load_parquet_speed(benchmark, tmp_path):
    """Benchmark loading postal codes from Parquet"""
    import pandas as pd

    parquet_file = tmp_path / "postal_codes.parquet"
    loader.export_parquet(parquet_file)

    def load_parquet():
        pd.read_parquet(parquet_file)

    benchmark(load_parquet)


@pytest.mark.benchmark
def test_load_spark_speed(benchmark):
    """Benchmark loading postal codes into Spark"""
    if not (is_spark_available() and is_java_available()):
        pytest.skip("Skipping Spark benchmark: PySpark or Java not available")

    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[1]")
        .appName("BenchmarkPostalLoader")
        .getOrCreate()
    )

    def load_spark():
        loader.load_spark(spark)

    benchmark(load_spark)
    spark.stop()
