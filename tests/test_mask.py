"""Tests for :func:`validkit.mask_secret`."""

import pytest

from validkit import mask_secret


class TestMaskSecret:
    """Normal, boundary and error cases for mask_secret."""

    @pytest.mark.parametrize(
        ("text", "keep", "expected"),
        [
            ("geheim123", 4, "*****m123"),
            ("geheim", 4, "**heim"),
            ("hunter2", 2, "*****r2"),
            ("topsecret", 3, "******ret"),
        ],
    )
    def test_masks_all_but_last_keep(self, text: str, keep: int, expected: str) -> None:
        assert mask_secret(text, keep) == expected

    @pytest.mark.parametrize(
        ("text", "keep"),
        [
            ("abc", 4),  # shorter than keep
            ("abcd", 4),  # equal to keep
            ("geheim123", 0),  # keep is zero
            ("geheim123", 20),  # keep greater than length
            ("", 4),  # empty text
        ],
    )
    def test_fully_masked(self, text: str, keep: int) -> None:
        assert mask_secret(text, keep) == "*" * len(text)

    def test_default_keep_is_four(self) -> None:
        assert mask_secret("geheim123") == "*****m123"

    def test_keep_zero_on_empty_text(self) -> None:
        assert mask_secret("", 0) == ""

    @pytest.mark.parametrize("keep", [-1, -4])
    def test_negative_keep_raises_value_error(self, keep: int) -> None:
        with pytest.raises(ValueError):
            mask_secret("geheim123", keep)

    @pytest.mark.parametrize("keep", [1.5, 4.0, None, "4"])
    def test_non_integer_keep_raises_type_error(self, keep: object) -> None:
        with pytest.raises(TypeError):
            mask_secret("geheim123", keep)  # type: ignore[arg-type]

    @pytest.mark.parametrize("text", [None, 12345, 3.14, ["geheim123"], b"geheim123"])
    def test_wrong_type_raises_type_error(self, text: object) -> None:
        with pytest.raises(TypeError):
            mask_secret(text)  # type: ignore[arg-type]

    def test_error_messages_do_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            mask_secret(12345)  # type: ignore[arg-type]
        assert "12345" not in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            mask_secret("geheim123", -1)
        assert "geheim123" not in str(excinfo.value)
