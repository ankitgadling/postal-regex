# Core validation and lookup functions
from .core import (
    validate,
    normalize,
    get_entry,
    get_country_regex,
    get_supported_countries,
)

# Bulk processing utilities for DataFrames and iterables
from .bulk import (
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

# Local analytics and statistics functions
from .analytics import (
    record_validation,
    show_stats,
    reset_stats,
    get_stats,
)

# Custom exception classes
from .errors import (
    PostalRegexError,
    CountryNotSupportedError,
    InvalidPostalCodeError,
    DataLoadError,
)

__all__ = [
    # Core
    "validate",
    "normalize",
    "get_entry",
    "get_country_regex",
    "get_supported_countries",
    # Bulk
    "bulk_validate",
    "bulk_normalize",
    "validate_dataframe",
    "validate_spark_dataframe",
    "load_json",
    "load_pandas",
    "load_spark",
    "export_csv",
    "export_parquet",
    # Analytics
    "record_validation",
    "show_stats",
    "reset_stats",
    "get_stats",
    # Exceptions
    "PostalRegexError",
    "CountryNotSupportedError",
    "InvalidPostalCodeError",
    "DataLoadError",
]
