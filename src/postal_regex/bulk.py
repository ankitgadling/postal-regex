from multiprocessing import Pool, cpu_count
import regex
from .validator import get_entry, normalize

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
        try:
            return bool(entry.regex.fullmatch(code, timeout=timeout))
        except regex.TimeoutError:
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
        return normalize(identifier)

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
    Validate postal codes in a Pandas or Dask DataFrame.
    Supports both in-memory (Pandas) and distributed (Dask) workflows.
    """
    import pandas as pd
    import dask.dataframe as dd

    is_dask = isinstance(df, dd.DataFrame)

    # Normalize countries
    def normalize_partition(part):
        part["country_norm"] = bulk_normalize(part[country_col], as_generator=False)
        return part

    df = df.map_partitions(normalize_partition) if is_dask else normalize_partition(df)

    # Validate postal codes per partition
    def validate_partition(part):
        part[output_col] = part.groupby("country_norm")[postal_col].transform(
            lambda group: bulk_validate(group.name, group, as_generator=False)
        )
        return part

    df = df.map_partitions(validate_partition) if is_dask else validate_partition(df)
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
    normalize_udf = udf(lambda c: bulk_normalize([c])[0], StringType())
    df = df.withColumn("country_norm", normalize_udf(col(country_col)))

    # Validate postal codes UDF
    validate_udf = udf(
        lambda country, postal: bulk_validate(country, [postal])[0],
        BooleanType()
    )
    df = df.withColumn(output_col, validate_udf(col("country_norm"), col(postal_col)))

    return df
