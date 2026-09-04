"""Tests for :func:`validkit.is_valid_email`."""

import time

import pytest

from validkit import is_valid_email


class TestIsValidEmail:
    """Normal, boundary, error and ReDoS-safety cases for is_valid_email."""

    @pytest.mark.parametrize(
        "address",
        [
            "alice@example.com",
            "john.doe@sub.example.co.uk",
            "user+tag@example.org",
            "user_name@example.com",
            "first.last@example.com",
            "User.Name@Example.COM",
            "12345@example.com",
            "a@b.co",
        ],
    )
    def test_valid_addresses(self, address: str) -> None:
        assert is_valid_email(address) is True

    @pytest.mark.parametrize(
        "address",
        [
            "",  # empty
            "aliceexample.com",  # missing @
            "alice@bob@example.com",  # more than one @
            "alice@example",  # missing dot
            "alice@exa mple.com",  # space in domain
            "alice@",  # empty domain
            "@example.com",  # empty local part
            "alice name@example.com",  # space in local part
            "alice@example .com",  # space before dot
            "alice@example!",  # invalid character in domain
        ],
    )
    def test_invalid_addresses(self, address: str) -> None:
        assert is_valid_email(address) is False

    @pytest.mark.parametrize(
        "bad",
        [
            None,
            12345,
            3.14,
            ["alice@example.com"],
            {"email": "alice@example.com"},
            b"alice@example.com",
        ],
    )
    def test_wrong_type_raises_type_error(self, bad: object) -> None:
        with pytest.raises(TypeError):
            is_valid_email(bad)  # type: ignore[arg-type]

    def test_type_error_message_does_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            is_valid_email(b"alice@example.com")  # type: ignore[arg-type]
        assert "alice" not in str(excinfo.value)
        assert "example.com" not in str(excinfo.value)

    def test_redos_safe_on_1000_char_input(self) -> None:
        # Long local part, long domain and a trailing character that cannot match:
        # the classic shape that triggers catastrophic backtracking on a naive regex.
        payload = "a" * 400 + "@" + "a" * 298 + "." + "a" * 299 + "!"
        assert len(payload) == 1000

        start = time.perf_counter()
        result = is_valid_email(payload)
        elapsed = time.perf_counter() - start

        assert result is False
        assert elapsed < 0.1
