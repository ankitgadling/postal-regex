from multiprocessing import Pool, cpu_count
import json
import importlib.resources as resources
from pathlib import Path
from typing import Union, Any, TYPE_CHECKING
import tempfile
from .core import get_entry, normalize, COUNTRY_INDEX

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
    """Validate an iterable of postal codes for a given country."""
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
    """Normalize an iterable of country identifiers to ISO alpha-2 codes."""

    def _norm(identifier):
        if identifier is None or not isinstance(identifier, str):
            return None
        try:
            return normalize(identifier)
        except ValueError:
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
    """Load postal codes as a list of dicts (raw JSON)."""
    with (
        resources.files("postal_regex.data")
        .joinpath("postal_codes.json")
        .open("r", encoding="utf-8") as f
    ):
        return json.load(f)


# ---------- Pandas Loader ----------
def load_pandas() -> "pd.DataFrame":
    """Load postal codes into a Pandas DataFrame."""
    import pandas as pd  # Lazy import

    return pd.DataFrame(load_json())


# ---------- Spark Loader ----------
def load_spark(spark_session: "pyspark.sql.SparkSession") -> "pyspark.sql.DataFrame":
    """Load postal codes into a Spark DataFrame."""

    data = load_json()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    return spark_session.read.json(tmp_path)


# ---------- Parquet Saver ----------
def export_parquet(output_path: Union[str, Path]) -> Path:
    """Export postal codes to a Parquet file."""

    df = load_pandas()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return output_path


# ---------- CSV Saver ----------
def export_csv(output_path: Union[str, Path]) -> Path:
    """Export postal codes to a CSV file."""

    df = load_pandas()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
