"""Tests for :func:`validkit.normalize_phone`."""

import pytest

from validkit import normalize_phone


class TestNormalizePhone:
    """Normal, boundary and error cases for normalize_phone."""

    @pytest.mark.parametrize(
        ("text", "country_code", "expected"),
        [
            ("030 1234567", "49", "+49301234567"),
            ("0301234567", "49", "+49301234567"),
            ("030-1234567", "49", "+49301234567"),
            ("(030) 123.45.67", "49", "+49301234567"),
            ("+49 30 1234567", "49", "+49301234567"),
            ("+49301234567", "49", "+49301234567"),
            ("+49 (30) 123-456.7", "49", "+49301234567"),
            ("0049 30 1234567", "49", "+49301234567"),
            ("0049301234567", "49", "+49301234567"),
            ("+1 (415) 555-0134", "49", "+14155550134"),
        ],
    )
    def test_normalization(self, text: str, country_code: str, expected: str) -> None:
        assert normalize_phone(text, country_code) == expected

    def test_existing_country_code_is_not_duplicated(self) -> None:
        assert normalize_phone("+49301234567", "49") == "+49301234567"
        assert normalize_phone("0049301234567", "49") == "+49301234567"
        assert "+4949" not in normalize_phone("+49301234567", "49")

    @pytest.mark.parametrize(
        ("text", "country_code", "expected"),
        [
            ("+1234567", "49", "+1234567"),  # 7 digits, country code already present
            ("12345", "49", "+4912345"),  # 7 digits, country code prepended
            ("+123456789012345", "49", "+123456789012345"),  # 15 digits
            ("1234567890123", "49", "+491234567890123"),  # 15 digits
        ],
    )
    def test_boundary_lengths_are_valid(self, text: str, country_code: str, expected: str) -> None:
        assert normalize_phone(text, country_code) == expected

    @pytest.mark.parametrize(
        ("text", "country_code"),
        [
            ("+123456", "49"),  # 6 digits — too short
            ("1234", "49"),  # 49 + 4 = 6 digits — too short
            ("+1234567890123456", "49"),  # 16 digits — too long
            ("12345678901234", "49"),  # 49 + 14 = 16 digits — too long
            ("", "49"),  # nothing to normalize
        ],
    )
    def test_out_of_range_length_raises_value_error(self, text: str, country_code: str) -> None:
        with pytest.raises(ValueError):
            normalize_phone(text, country_code)

    @pytest.mark.parametrize(
        ("text", "country_code"),
        [
            (None, "49"),
            (12345, "49"),
            (3.14, "49"),
            (["+49 30 1234567"], "49"),
            (b"030 1234567", "49"),
            ("030 1234567", 49),
            ("030 1234567", 4.9),
        ],
    )
    def test_wrong_type_raises_type_error(self, text: object, country_code: object) -> None:
        with pytest.raises(TypeError):
            normalize_phone(text, country_code)  # type: ignore[arg-type]

    @pytest.mark.parametrize("country_code", [None, "", "   "])
    def test_missing_or_empty_country_code_raises_value_error(self, country_code: object) -> None:
        with pytest.raises(ValueError):
            normalize_phone("030 1234567", country_code)  # type: ignore[arg-type]

    def test_error_messages_do_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            normalize_phone(12345, "49")  # type: ignore[arg-type]
        assert "12345" not in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            normalize_phone("030 1234567", "")
        assert "030" not in str(excinfo.value)
        assert "1234567" not in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            normalize_phone("+123456", "49")
        assert "123456" not in str(excinfo.value)
