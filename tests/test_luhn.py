"""Tests for :func:`validkit.luhn_check`."""

import pytest

from validkit import luhn_check


class TestLuhnCheck:
    """Normal, boundary and error cases for luhn_check."""

    @pytest.mark.parametrize(
        "digits",
        [
            "79927398713",
            "378282246310005",
            "5555555555554444",
            "4111111111111111",
            "0",
        ],
    )
    def test_valid_numbers(self, digits: str) -> None:
        assert luhn_check(digits) is True

    @pytest.mark.parametrize(
        "digits",
        [
            "79927398712",
            "7992739871",
            "799273987131",
            "1234567890",
        ],
    )
    def test_invalid_numbers(self, digits: str) -> None:
        assert luhn_check(digits) is False

    @pytest.mark.parametrize(
        "digits",
        [
            "7992 7398 713",
            "7992-7398-713",
            "7992 7398-713",
            "7 9 9 2 7 3 9 8 7 1 3",
        ],
    )
    def test_ignores_spaces_and_hyphens(self, digits: str) -> None:
        assert luhn_check(digits) is True

    @pytest.mark.parametrize(
        "digits",
        [
            "",
            "   ",
            "----",
            "- - ",
            "7992 7398 712",
        ],
    )
    def test_empty_or_separator_only_is_false(self, digits: str) -> None:
        assert luhn_check(digits) is False

    def test_int_input_valid(self) -> None:
        assert luhn_check(79927398713) is True

    def test_int_input_invalid(self) -> None:
        assert luhn_check(79927398712) is False

    @pytest.mark.parametrize(
        "digits",
        [
            "7992739871a",
            "7992739871!",
            "7992739871.3",
            "79927398713\n",
            "79 927398713x",
        ],
    )
    def test_non_numeric_characters_are_false(self, digits: str) -> None:
        assert luhn_check(digits) is False

    @pytest.mark.parametrize(
        "digits",
        [
            None,
            True,
            False,
            3.14,
            ["79927398713"],
            {"n": 79927398713},
            b"79927398713",
        ],
    )
    def test_wrong_type_raises_type_error(self, digits: object) -> None:
        with pytest.raises(TypeError):
            luhn_check(digits)  # type: ignore[arg-type]

    def test_negative_int_is_false(self) -> None:
        assert luhn_check(-79927398713) is False

    def test_type_error_message_does_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            luhn_check(b"79927398713")  # type: ignore[arg-type]
        assert "79927398713" not in str(excinfo.value)
