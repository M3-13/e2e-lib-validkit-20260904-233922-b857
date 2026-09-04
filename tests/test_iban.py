"""Tests for :func:`validkit.is_valid_iban`."""

import time

import pytest

from validkit import is_valid_iban


class TestIsValidIban:
    """Normal, boundary, error and ReDoS-safety cases for is_valid_iban."""

    @pytest.mark.parametrize(
        "iban",
        [
            "DE89 3704 0044 0532 0130 00",
            "DE89370400440532013000",
            "GB29 NWBK 6016 1331 9268 19",
            "FR14 2004 1010 0505 0001 3M02 606",
            "ES91 2100 0418 4502 0005 1332",
            "NL91 ABNA 0417 1643 00",
            "CH93 0076 2011 6238 5295 7",
            "IT60 X054 2811 1010 0000 0123 456",
        ],
    )
    def test_valid_ibans(self, iban: str) -> None:
        assert is_valid_iban(iban) is True

    @pytest.mark.parametrize(
        "iban",
        [
            "DE89 3704 0044 0532 0130 01",  # one digit changed
            "DE88 3704 0044 0532 0130 00",  # check digits changed
            "DE89 3704 0044 0532 0130 10",  # one digit changed
            "GB29 NWBK 6016 1331 9268 18",  # one digit changed
        ],
    )
    def test_wrong_checksum_is_false(self, iban: str) -> None:
        assert is_valid_iban(iban) is False

    @pytest.mark.parametrize(
        "iban",
        [
            "",  # empty
            "   ",  # whitespace only
            "DE89 3704 0044 0532 0130",  # truncated (missing the two check digits)
            "DE89 3704 0044 0532 0130 001",  # extra trailing digit
            "DE89 3704 0044 0",  # too short (13 chars, below the 15-char minimum)
            "DE89 3704 0044 0532 0130 0000 0000 0000 0000",  # too long (36 chars, above 34)
            "DE89 3704 0044 0532 0130 0O",  # letter O instead of digit 0
            "DE89 3704 0044 0532 0130 0!",  # invalid punctuation
            "de89 3704 0044 0532 0130 00",  # lower-case country code
            "DE89-3704-0044-0532-0130-00",  # hyphens are not ignored
        ],
    )
    def test_invalid_ibans(self, iban: str) -> None:
        assert is_valid_iban(iban) is False

    @pytest.mark.parametrize(
        "bad",
        [
            None,
            890370400440532013000,
            3.14,
            ["DE89 3704 0044 0532 0130 00"],
            {"iban": "DE89 3704 0044 0532 0130 00"},
            b"DE89 3704 0044 0532 0130 00",
        ],
    )
    def test_wrong_type_raises_type_error(self, bad: object) -> None:
        with pytest.raises(TypeError):
            is_valid_iban(bad)  # type: ignore[arg-type]

    def test_type_error_message_does_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            is_valid_iban(b"DE89 3704 0044 0532 0130 00")  # type: ignore[arg-type]
        assert "DE89" not in str(excinfo.value)
        assert "3704" not in str(excinfo.value)

    def test_redos_safe_on_1000_char_input(self) -> None:
        # A plausible prefix followed by a very long trailing run: the shape that
        # triggers catastrophic backtracking on a naive, nested-quantifier regex.
        payload = "DE89" + "A" * 996
        assert len(payload) == 1000

        start = time.perf_counter()
        result = is_valid_iban(payload)
        elapsed = time.perf_counter() - start

        assert result is False
        assert elapsed < 0.1
