"""Tests for :func:`validkit.strip_accents`."""

import pytest

from validkit import strip_accents


class TestStripAccents:
    """Normal, boundary and error cases for strip_accents."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("München café naïve", "Munchen cafe naive"),
            ("Über Ökonomie", "Uber Okonomie"),
            ("ÀÉÎÕÜ", "AEIOU"),
            ("àéîõü", "aeiou"),
            ("Zoë ñ", "Zoe n"),
        ],
    )
    def test_accents_are_removed(self, text: str, expected: str) -> None:
        assert strip_accents(text) == expected

    @pytest.mark.parametrize(
        "text",
        [
            "Munchen cafe naive",
            "plain ascii",
            "",
            " ",
            "12345",
            "!@#$%^&*()",
        ],
    )
    def test_unchanged_input_without_accents(self, text: str) -> None:
        assert strip_accents(text) == text

    def test_combining_character_is_removed(self) -> None:
        # "e" + U+0301 COMBINING ACUTE ACCENT decomposes to a single "e".
        assert strip_accents("e\u0301") == "e"

    def test_special_case_sharp_s_is_preserved(self) -> None:
        # "ß" has no NFD decomposition and is not a combining mark, so it stays.
        assert strip_accents("Straße") == "Straße"

    @pytest.mark.parametrize("text", [None, 42, 3.14, b"cafe", ["caf\xe9"]])
    def test_wrong_type_raises_type_error(self, text: object) -> None:
        with pytest.raises(TypeError):
            strip_accents(text)  # type: ignore[arg-type]

    def test_error_messages_do_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            strip_accents(12345)  # type: ignore[arg-type]
        assert "12345" not in str(excinfo.value)
