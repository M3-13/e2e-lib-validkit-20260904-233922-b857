"""Tests for :func:`validkit.slugify`."""

import time

import pytest

from validkit import slugify


class TestSlugify:
    """Normal, boundary, error and ReDoS-safety cases for slugify."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Héllo Wörld! -- Foo_ Bar", "hello-world-foo-bar"),
            ("Hello World", "hello-world"),
            ("HELLO WORLD", "hello-world"),
            ("hello  world", "hello-world"),
            ("  padded  ", "padded"),
            ("---dashes---", "dashes"),
            ("under_score and-dash", "under-score-and-dash"),
            ("foo.bar/baz", "foo-bar-baz"),
            ("123 456", "123-456"),
        ],
    )
    def test_slug_creation(self, text: str, expected: str) -> None:
        assert slugify(text) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Über Ökonomie", "uber-okonomie"),
            ("ÀÉÎÕÜ", "aeiou"),
            ("àéîõü", "aeiou"),
            ("München café naïve", "munchen-cafe-naive"),
        ],
    )
    def test_umlauts_and_accents_are_slugified(self, text: str, expected: str) -> None:
        assert slugify(text) == expected

    @pytest.mark.parametrize(
        "text",
        [
            "!!!",
            "$$$",
            "___",
            "   ",
            "---",
            "",
            "@#$%^&*()",
        ],
    )
    def test_only_special_chars_yield_empty_slug(self, text: str) -> None:
        assert slugify(text) == ""

    @pytest.mark.parametrize("text", [None, 42, 3.14, b"hello", ["hello"]])
    def test_wrong_type_raises_type_error(self, text: object) -> None:
        with pytest.raises(TypeError):
            slugify(text)  # type: ignore[arg-type]

    def test_type_error_message_does_not_leak_input(self) -> None:
        with pytest.raises(TypeError) as excinfo:
            slugify(b"H\xe9llo")  # type: ignore[arg-type]
        assert "Héllo" not in str(excinfo.value)

    def test_redos_safe_on_1000_char_input(self) -> None:
        # A long run of non-alphanumeric characters that a naive regex could
        # backtrack over catastrophically; the linear expression must finish fast.
        payload = "!" * 1000
        assert len(payload) == 1000

        start = time.perf_counter()
        result = slugify(payload)
        elapsed = time.perf_counter() - start

        assert result == ""
        assert elapsed < 0.1
