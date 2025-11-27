"""
Custom exception classes for postal-regex.

This module provides a base exception class and specific exception types
for different error scenarios in postal code validation.
"""


class PostalRegexError(Exception):
    """
    Base exception class for all postal-regex errors.

    All custom exceptions in this module inherit from this class,
    making it easy to catch any postal-regex related error.

    Example:
        >>> try:
        ...     validate("XX", "12345")
        ... except PostalRegexError as e:
        ...     print(f"Postal regex error: {e}")
    """


class CountryNotSupportedError(PostalRegexError):
    """
    Raised when a country code or name is not recognized.

    This exception is raised when attempting to validate or normalize
    a country identifier that is not in the supported countries list.

    Attributes:
        country_identifier: The country code or name that was not found.
        message: A descriptive error message.

    Example:
        >>> try:
        ...     normalize("XX")
        ... except CountryNotSupportedError as e:
        ...     print(f"Country '{e.country_identifier}' is not supported")
    """

    def __init__(self, country_identifier: str, message: str = None):
        """
        Initialize CountryNotSupportedError.

        Args:
            country_identifier: The country code or name that was not found.
            message: Optional custom error message. If not provided,
                    a default message will be generated.
        """
        self.country_identifier = country_identifier
        if message is None:
            message = (
                f"Country '{country_identifier}' is not supported. "
                f"Use get_supported_countries() to see available countries."
            )
        super().__init__(message)


class InvalidPostalCodeError(PostalRegexError):
    """
    Raised when a postal code fails regex validation.

    This exception can be raised when a postal code does not match
    the expected format for a given country.

    Attributes:
        country_identifier: The country code or name for which validation failed.
        postal_code: The postal code that failed validation.
        message: A descriptive error message.

    Example:
        >>> try:
        ...     validate_strict("US", "INVALID")
        ... except InvalidPostalCodeError as e:
        ...     print(f"Postal code '{e.postal_code}' is invalid "
        ...           f"for {e.country_identifier}")
    """

    def __init__(self, country_identifier: str, postal_code: str, message: str = None):
        """
        Initialize InvalidPostalCodeError.

        Args:
            country_identifier: The country code or name for which validation failed.
            postal_code: The postal code that failed validation.
            message: Optional custom error message. If not provided,
                    a default message will be generated.
        """
        self.country_identifier = country_identifier
        self.postal_code = postal_code
        if message is None:
            message = (
                f"Postal code '{postal_code}' is invalid "
                f"for country '{country_identifier}'."
            )
        super().__init__(message)


class DataLoadError(PostalRegexError):
    """
    Raised when postal_codes.json is missing or corrupted.

    This exception is raised when the postal codes data file cannot be
    loaded or parsed, typically due to:
    - Missing file
    - Corrupted JSON
    - Invalid file format
    - Permission errors

    Attributes:
        file_path: The path to the file that failed to load.
        original_error: The original exception that occurred during loading.
        message: A descriptive error message.

    Example:
        >>> try:
        ...     load_data()
        ... except DataLoadError as e:
        ...     print(f"Failed to load data from {e.file_path}: {e.original_error}")
    """

    def __init__(
        self, file_path: str, original_error: Exception = None, message: str = None
    ):
        """
        Initialize DataLoadError.

        Args:
            file_path: The path to the file that failed to load.
            original_error: Optional original exception that occurred.
            message: Optional custom error message. If not provided,
                    a default message will be generated.
        """
        self.file_path = file_path
        self.original_error = original_error
        if message is None:
            base_msg = f"Failed to load postal codes data from '{file_path}'."
            if original_error:
                base_msg += (
                    f" Original error: {type(original_error).__name__}: "
                    f"{original_error}"
                )
            message = base_msg
        super().__init__(message)
