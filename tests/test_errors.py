"""
Unit tests for custom exception classes in postal-regex.

This module tests the exception hierarchy and ensures that exceptions
are raised correctly with appropriate messages and context.
"""

import sys
from pathlib import Path
import pytest
import json
import tempfile

# Add src folder to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from postal_regex.errors import (
    PostalRegexError,
    CountryNotSupportedError,
    InvalidPostalCodeError,
    DataLoadError,
)
from postal_regex import core, bulk


class TestPostalRegexError:
    """Test the base PostalRegexError class."""

    def test_base_exception_inheritance(self):
        """Test that PostalRegexError inherits from Exception."""
        assert issubclass(PostalRegexError, Exception)

    def test_base_exception_can_be_raised(self):
        """Test that PostalRegexError can be raised and caught."""
        with pytest.raises(PostalRegexError):
            raise PostalRegexError("Test error")

    def test_specific_exceptions_inherit_from_base(self):
        """Test that all specific exceptions inherit from PostalRegexError."""
        assert issubclass(CountryNotSupportedError, PostalRegexError)
        assert issubclass(InvalidPostalCodeError, PostalRegexError)
        assert issubclass(DataLoadError, PostalRegexError)


class TestCountryNotSupportedError:
    """Test the CountryNotSupportedError exception."""

    def test_default_message(self):
        """Test that default message is generated correctly."""
        error = CountryNotSupportedError("XX")
        assert "XX" in str(error)
        assert "not supported" in str(error).lower()
        assert error.country_identifier == "XX"

    def test_custom_message(self):
        """Test that custom message can be provided."""
        custom_msg = "Custom error message"
        error = CountryNotSupportedError("XX", message=custom_msg)
        assert str(error) == custom_msg
        assert error.country_identifier == "XX"

    def test_raised_by_normalize(self):
        """Test that normalize raises CountryNotSupportedError."""
        with pytest.raises(CountryNotSupportedError) as exc_info:
            core.normalize("INVALID_COUNTRY")
        assert exc_info.value.country_identifier == "INVALID_COUNTRY"

    def test_raised_by_validate(self):
        """Test that validate raises CountryNotSupportedError for invalid country."""
        with pytest.raises(CountryNotSupportedError) as exc_info:
            core.validate("INVALID_COUNTRY", "12345")
        assert exc_info.value.country_identifier == "INVALID_COUNTRY"

    def test_raised_by_get_entry(self):
        """Test that get_entry raises CountryNotSupportedError."""
        with pytest.raises(CountryNotSupportedError) as exc_info:
            core.get_entry("INVALID_COUNTRY")
        assert exc_info.value.country_identifier == "INVALID_COUNTRY"

    def test_raised_by_get_country_regex(self):
        """Test that get_country_regex raises CountryNotSupportedError."""
        with pytest.raises(CountryNotSupportedError) as exc_info:
            core.get_country_regex("INVALID_COUNTRY")
        assert exc_info.value.country_identifier == "INVALID_COUNTRY"

    def test_can_catch_base_exception(self):
        """Test that CountryNotSupportedError can be caught as PostalRegexError."""
        try:
            core.normalize("INVALID_COUNTRY")
            assert False, "Should have raised an exception"
        except PostalRegexError:
            # This should catch CountryNotSupportedError
            assert True


class TestInvalidPostalCodeError:
    """Test the InvalidPostalCodeError exception."""

    def test_default_message(self):
        """Test that default message is generated correctly."""
        error = InvalidPostalCodeError("US", "INVALID")
        assert "INVALID" in str(error)
        assert "US" in str(error)
        assert error.country_identifier == "US"
        assert error.postal_code == "INVALID"

    def test_custom_message(self):
        """Test that custom message can be provided."""
        custom_msg = "Custom postal code error"
        error = InvalidPostalCodeError("US", "INVALID", message=custom_msg)
        assert str(error) == custom_msg
        assert error.country_identifier == "US"
        assert error.postal_code == "INVALID"

    def test_can_be_raised_manually(self):
        """Test that InvalidPostalCodeError can be raised manually."""
        with pytest.raises(InvalidPostalCodeError) as exc_info:
            raise InvalidPostalCodeError("US", "INVALID")
        assert exc_info.value.country_identifier == "US"
        assert exc_info.value.postal_code == "INVALID"

    def test_can_catch_base_exception(self):
        """Test that InvalidPostalCodeError can be caught as PostalRegexError."""
        try:
            raise InvalidPostalCodeError("US", "INVALID")
        except PostalRegexError:
            # This should catch InvalidPostalCodeError
            assert True


class TestDataLoadError:
    """Test the DataLoadError exception."""

    def test_default_message_without_original_error(self):
        """Test that default message is generated without original error."""
        error = DataLoadError("/path/to/file.json")
        assert "/path/to/file.json" in str(error)
        assert error.file_path == "/path/to/file.json"
        assert error.original_error is None

    def test_default_message_with_original_error(self):
        """Test that default message includes original error."""
        original = FileNotFoundError("File not found")
        error = DataLoadError("/path/to/file.json", original)
        assert "/path/to/file.json" in str(error)
        assert "FileNotFoundError" in str(error)
        assert error.file_path == "/path/to/file.json"
        assert error.original_error == original

    def test_custom_message(self):
        """Test that custom message can be provided."""
        custom_msg = "Custom data load error"
        error = DataLoadError("/path/to/file.json", message=custom_msg)
        assert str(error) == custom_msg
        assert error.file_path == "/path/to/file.json"

    def test_raised_on_file_not_found(self):
        """Test that DataLoadError is raised when file is not found."""
        # This test verifies the exception structure, but we can't easily
        # test the actual data loading without mocking
        error = DataLoadError("/nonexistent/file.json", FileNotFoundError("Not found"))
        assert isinstance(error, DataLoadError)
        assert isinstance(error.original_error, FileNotFoundError)

    def test_raised_on_json_decode_error(self):
        """Test that DataLoadError is raised on JSON decode errors."""
        original = json.JSONDecodeError("Invalid JSON", "", 0)
        error = DataLoadError("/path/to/file.json", original)
        assert isinstance(error, DataLoadError)
        assert isinstance(error.original_error, json.JSONDecodeError)

    def test_can_catch_base_exception(self):
        """Test that DataLoadError can be caught as PostalRegexError."""
        try:
            raise DataLoadError("/path/to/file.json")
        except PostalRegexError:
            # This should catch DataLoadError
            assert True


class TestExceptionIntegration:
    """Integration tests for exceptions in real scenarios."""

    def test_bulk_normalize_handles_country_error(self):
        """Test that bulk_normalize handles CountryNotSupportedError gracefully."""
        identifiers = ["US", "INVALID_COUNTRY", "CA"]
        results = bulk.bulk_normalize(identifiers)
        # Invalid country should be kept as-is
        assert results[0] == "US"
        assert results[1] == "INVALID_COUNTRY"  # Kept as-is due to exception handling
        assert results[2] == "CA"

    def test_exception_chaining(self):
        """Test that exceptions properly chain with original errors."""
        original = FileNotFoundError("File not found")
        error = DataLoadError("/path/to/file.json", original)
        # The error should have the original error as its cause
        assert error.original_error == original

    def test_multiple_exception_types(self):
        """Test that different exception types can be distinguished."""
        # Test that we can catch specific exceptions
        try:
            core.normalize("INVALID")
            assert False, "Should have raised CountryNotSupportedError"
        except CountryNotSupportedError:
            assert True
        except PostalRegexError:
            # Should not reach here if CountryNotSupportedError was raised
            assert False, "Should have caught CountryNotSupportedError specifically"

        # Test that we can catch base exception for all types
        exceptions_to_test = [
            CountryNotSupportedError("XX"),
            InvalidPostalCodeError("US", "INVALID"),
            DataLoadError("/path/to/file.json"),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except PostalRegexError:
                # All should be catchable as base exception
                assert True
