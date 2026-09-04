"""Tests for :func:`validkit.is_valid_isbn13`."""

import time

import pytest

from validkit import is_valid_isbn13


class TestIsValidIsbn13:
    """Normal, boundary, error and ReDoS-safety cases for is_valid_isbn13."""

    @pytest.mark.parametrize(
        "isbn",
        [
            "978-3-16-148410-0",
            "9783161484100",
            "978-0-306-40615-7",
            "9780306406157",
            "978-1-86197-876-9",
        ],
    )
    def test_valid_isbns(self, isbn: str) -> None:
        assert is_valid_isbn13(isbn) is True

    def test_valid_isbn_with_spaces(self) -> None:
        assert is_valid_isbn13("978 3 16 148410 0") is True

    @pytest.mark.parametrize(
        "isbn",
        [
            "978-3-16-148410-1",  # wrong check digit
            "978-3-16-148410-2",  # wrong check digit
            "9783161484109",  # wrong check digit
        ],
    )
    def test_wrong_check_digit_is_false(self, isbn: str) -> None:
        assert is_valid_isbn13(isbn) is False

    @pytest.mark.parametrize(
        "isbn",
        [
            "",  # empty
            "   ",  # whitespace only
            "--- ",  # separators only
            "978-3-16-148410",  # 12 digits (missing check digit)
            "978316148410",  # 12 digits
            "978-3-16-148410-00",  # 14 digits
            "97831614841000",  # 14 digits
        ],
    )
    def test_invalid_length_is_false(self, isbn: str) -> None:
        assert is_valid_isbn13(isbn) is False

    @pytest.mark.parametrize(
        "isbn",
        [
            "978-3-16-14841O-0",  # letter O instead of digit 0
            "978-3-16-148410-x",  # letter check digit
            "978-3-16-148410-0!",  # punctuation
            "978-3-16-14841A-0",  # letter inside
            "978-3-16-148410-0\n",  # trailing newline
        ],
    )
    def test_non_numeric_characters_are_false(self, isbn: str) -> None:
        assert is_valid_isbn13(isbn) is False

    @pytest.mark.parametrize(
        "bad",
        [
            None,
            9783161484100,
            3.14,
            ["978-3-16-148410-0"],
            {"isbn": "978-3-16-148410-0"},
            b"978-3-16-148410-0",
        ],
    )
    def test_wrong_type_raises_type_error(self, bad: object) -> None:
        with pytest.raises(TypeError):
            is_valid_isbn13(bad)  # type: ignore[arg-type]

    def test_type_error_message_does_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            is_valid_isbn13(b"978-3-16-148410-0")  # type: ignore[arg-type]
        assert "978" not in str(excinfo.value)
        assert "148410" not in str(excinfo.value)

    def test_redos_safe_on_1000_char_input(self) -> None:
        # A plausible prefix followed by a very long trailing run that cannot
        # match the fixed 13-digit count: the shape that triggers catastrophic
        # backtracking on a naive, nested-quantifier regex.
        payload = "978-" + "1" * 996
        assert len(payload) == 1000

        start = time.perf_counter()
        result = is_valid_isbn13(payload)
        elapsed = time.perf_counter() - start

        assert result is False
        assert elapsed < 0.1
