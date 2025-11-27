from multiprocessing import Pool, cpu_count
import json
import importlib.resources as resources
from pathlib import Path
from typing import Union, Any, TYPE_CHECKING
import tempfile
from .core import get_entry, normalize, COUNTRY_INDEX
from .errors import CountryNotSupportedError, DataLoadError

if TYPE_CHECKING:
    import pandas as pd
    import pyspark.sql


# ---------------------------
# Core Bulk Functions
# ---------------------------
def bulk_validate(
    country_identifier: str,
    postal_codes,
    timeout: float = 0.1,
    parallel: bool = False,
    workers: int = None,
    as_generator: bool = False,
):
    """
    Validate an iterable of postal codes for a given country.

    Args:
        country_identifier: Country code (e.g., "US") or country name (e.g., "United States").
        postal_codes: An iterable of postal codes to validate.
        timeout: Maximum time (in seconds) to spend on regex matching per code. Default is 0.1 seconds.
        parallel: If True, use multiprocessing for parallel validation.
        workers: Number of worker processes (defaults to CPU count if parallel=True).
        as_generator: If True, return a generator instead of a list.

    Returns:
        A list or generator of boolean values indicating validation results.

    Raises:
        CountryNotSupportedError: If the country identifier is not recognized.

    Example:
        >>> results = bulk_validate("US", ["90210", "10001", "INVALID"])
        >>> list(results)
        [True, True, False]
    """
    entry = get_entry(country_identifier)

    def _check(code):
        if code is None or not isinstance(code, str):
            return False  # missing or non-string -> invalid
        try:
            return bool(entry.regex.fullmatch(code, timeout=timeout))
        except AttributeError:
            # fallback if regex.TimeoutError does not exist
            return False

    if parallel:
        nproc = workers or cpu_count()
        with Pool(processes=nproc) as pool:
            results = pool.map(_check, postal_codes)
    else:
        results = map(_check, postal_codes)

    if as_generator:
        return ((pc, res) for pc, res in zip(postal_codes, results))
    else:
        return list(results)


def bulk_normalize(
    identifiers,
    parallel: bool = False,
    workers: int = None,
    as_generator: bool = False,
):
    """
    Normalize an iterable of country identifiers to ISO alpha-2 codes.

    Unknown country identifiers are kept as-is (not raised as exceptions).

    Args:
        identifiers: An iterable of country codes or names to normalize.
        parallel: If True, use multiprocessing for parallel normalization.
        workers: Number of worker processes (defaults to CPU count if parallel=True).
        as_generator: If True, return a generator instead of a list.

    Returns:
        A list or generator of normalized country codes. Unknown identifiers
        are returned unchanged.

    Example:
        >>> results = bulk_normalize(["US", "United States", "INVALID"])
        >>> list(results)
        ['US', 'US', 'INVALID']
    """

    def _norm(identifier):
        if identifier is None or not isinstance(identifier, str):
            return None
        try:
            return normalize(identifier)
        except CountryNotSupportedError:
            return identifier  # unknown country -> keep as-is

    if parallel:
        nproc = workers or cpu_count()
        with Pool(processes=nproc) as pool:
            results = pool.map(_norm, identifiers)
    else:
        results = map(_norm, identifiers)

    if as_generator:
        return ((idn, res) for idn, res in zip(identifiers, results))
    else:
        return list(results)


# ---------------------------
# Pandas/Dask Wrapper
# ---------------------------
def validate_dataframe(df, country_col, postal_col, output_col="is_valid"):
    """
    Validate postal codes in a Pandas or Dask DataFrame using precompiled regex lookup.
    Fully vectorized per partition for scalability, preserves None/NaN values.

    Args:
        df: A Pandas or Dask DataFrame containing postal code data.
        country_col: Name of the column containing country identifiers.
        postal_col: Name of the column containing postal codes.
        output_col: Name of the column to store validation results. Default is "is_valid".

    Returns:
        The DataFrame with a new column containing validation results.

    Raises:
        ImportError: If neither pandas nor dask is installed.
        TypeError: If df is not a Pandas or Dask DataFrame.
        CountryNotSupportedError: If any country identifier in the DataFrame is not recognized
                                 (though this is handled gracefully by returning False for invalid countries).

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"country": ["US", "CA"], "postal": ["90210", "K1A 0B1"]})
        >>> result = validate_dataframe(df, "country", "postal")
        >>> result["is_valid"].tolist()
        [True, True]
    """
    # -----------------------------
    # Lazy imports
    # -----------------------------
    try:
        import pandas as pd
    except ImportError:
        pd = None

    try:
        import dask.dataframe as dd
    except ImportError:
        dd = None

    if pd is None and dd is None:
        raise ImportError(
            "Either pandas or dask must be installed to use this function."
        )

    # Detect type
    is_dask = dd is not None and isinstance(df, dd.DataFrame)
    is_pandas = pd is not None and isinstance(df, pd.DataFrame)

    if not (is_dask or is_pandas):
        raise TypeError("df must be a Pandas or Dask DataFrame")

    # -----------------------------
    # Normalize country names safely
    # -----------------------------
    def normalize_partition(part):
        part["country_norm"] = part[country_col].apply(
            lambda c: None if pd.isna(c) else str(c).upper()
        )
        return part

    df = df.map_partitions(normalize_partition) if is_dask else normalize_partition(df)

    # Initialize output column
    df[output_col] = False

    # -----------------------------
    # Vectorized validation per country
    # -----------------------------
    for country_name, record in COUNTRY_INDEX.items():
        mask = df["country_norm"] == country_name.upper()
        if is_dask:
            # Dask: apply per partition
            def apply_mask(part, mask_series):
                idx = mask_series.loc[part.index]
                if idx.any():
                    part.loc[idx, output_col] = (
                        part.loc[idx, postal_col]
                        .astype(str)
                        .str.fullmatch(record.regex.pattern)
                    )
                return part

            df = df.map_partitions(apply_mask, mask)
        else:
            # Pandas: vectorized
            df.loc[mask, output_col] = (
                df.loc[mask, postal_col].astype(str).str.fullmatch(record.regex.pattern)
            )

    return df


# ---------------------------
# Spark Wrapper
# ---------------------------
def validate_spark_dataframe(df, country_col, postal_col, output_col="is_valid"):
    """
    Validate postal codes in a Spark DataFrame using UDFs.

    Args:
        df: A Spark DataFrame containing postal code data.
        country_col: Name of the column containing country identifiers.
        postal_col: Name of the column containing postal codes.
        output_col: Name of the column to store validation results. Default is "is_valid".

    Returns:
        The Spark DataFrame with a new column containing validation results.

    Raises:
        ImportError: If pyspark is not installed.
        CountryNotSupportedError: If any country identifier is not recognized
                                 (though this is handled gracefully by returning False for invalid countries).

    Example:
        >>> from pyspark.sql import SparkSession
        >>> spark = SparkSession.builder.appName("test").getOrCreate()
        >>> df = spark.createDataFrame([("US", "90210"), ("CA", "K1A 0B1")], ["country", "postal"])
        >>> result = validate_spark_dataframe(df, "country", "postal")
    """
    from pyspark.sql.functions import col, udf
    from pyspark.sql.types import BooleanType, StringType

    # Normalize countries UDF
    normalize_udf = udf(
        lambda c: bulk_normalize([c])[0] if c is not None else None, StringType()
    )
    df = df.withColumn("country_norm", normalize_udf(col(country_col)))

    # Validate postal codes UDF
    validate_udf = udf(
        lambda country, postal: (
            bool(bulk_validate(country, [postal])[0]) if postal is not None else False
        ),
        BooleanType(),
    )
    df = df.withColumn(output_col, validate_udf(col("country_norm"), col(postal_col)))

    return df


# ---------- Core JSON Loader ----------
def load_json() -> list[dict[str, Any]]:
    """
    Load postal codes as a list of dicts (raw JSON).

    Returns:
        A list of dictionaries containing postal code data for each country.

    Raises:
        DataLoadError: If the postal_codes.json file is missing or corrupted.

    Example:
        >>> data = load_json()
        >>> len(data) > 0
        True
    """
    data_file = resources.files("postal_regex.data").joinpath("postal_codes.json")
    try:
        with data_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise DataLoadError(str(data_file), e) from e
    except json.JSONDecodeError as e:
        raise DataLoadError(str(data_file), e) from e
    except Exception as e:
        raise DataLoadError(str(data_file), e) from e


# ---------- Pandas Loader ----------
def load_pandas() -> "pd.DataFrame":
    """
    Load postal codes into a Pandas DataFrame.

    Returns:
        A Pandas DataFrame containing postal code data for all supported countries.

    Raises:
        DataLoadError: If the postal_codes.json file is missing or corrupted.
        ImportError: If pandas is not installed.

    Example:
        >>> df = load_pandas()
        >>> "country_code" in df.columns
        True
    """
    import pandas as pd  # Lazy import

    return pd.DataFrame(load_json())


# ---------- Spark Loader ----------
def load_spark(spark_session: "pyspark.sql.SparkSession") -> "pyspark.sql.DataFrame":
    """
    Load postal codes into a Spark DataFrame.

    Args:
        spark_session: An active SparkSession instance.

    Returns:
        A Spark DataFrame containing postal code data for all supported countries.

    Raises:
        DataLoadError: If the postal_codes.json file is missing or corrupted.
        ImportError: If pyspark is not installed.

    Example:
        >>> from pyspark.sql import SparkSession
        >>> spark = SparkSession.builder.appName("test").getOrCreate()
        >>> df = load_spark(spark)
    """

    data = load_json()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    return spark_session.read.json(tmp_path)


# ---------- Parquet Saver ----------
def export_parquet(output_path: Union[str, Path]) -> Path:
    """
    Export postal codes to a Parquet file.

    Args:
        output_path: Path where the Parquet file should be saved.

    Returns:
        The Path object of the saved file.

    Raises:
        DataLoadError: If the postal_codes.json file is missing or corrupted.
        ImportError: If pandas or pyarrow is not installed.

    Example:
        >>> path = export_parquet("postal_codes.parquet")
    """

    df = load_pandas()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return output_path


# ---------- CSV Saver ----------
def export_csv(output_path: Union[str, Path]) -> Path:
    """
    Export postal codes to a CSV file.

    Args:
        output_path: Path where the CSV file should be saved.

    Returns:
        The Path object of the saved file.

    Raises:
        DataLoadError: If the postal_codes.json file is missing or corrupted.
        ImportError: If pandas is not installed.

    Example:
        >>> path = export_csv("postal_codes.csv")
    """

    df = load_pandas()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
