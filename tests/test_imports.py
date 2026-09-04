"""Smoke tests: all nine names import and expose the agreed signatures."""

import inspect

import validkit


def _params(name: str) -> inspect.Signature:
    return inspect.signature(getattr(validkit, name))


def test_all_nine_names_are_exported() -> None:
    expected = {
        "is_valid_email",
        "luhn_check",
        "is_valid_iban",
        "is_valid_isbn13",
        "normalize_phone",
        "strip_accents",
        "mask_secret",
        "slugify",
        "clamp",
    }
    assert expected.issubset(set(validkit.__all__))
    for name in expected:
        assert hasattr(validkit, name)


def test_signatures_match_the_contract() -> None:
    assert _params("is_valid_email").return_annotation is bool
    assert str(_params("is_valid_email")) == "(text: str) -> bool"

    assert _params("luhn_check").return_annotation is bool
    assert str(_params("luhn_check")) == "(digits: str | int) -> bool"

    assert _params("is_valid_iban").return_annotation is bool
    assert str(_params("is_valid_iban")) == "(text: str) -> bool"

    assert _params("is_valid_isbn13").return_annotation is bool
    assert str(_params("is_valid_isbn13")) == "(text: str) -> bool"

    assert _params("normalize_phone").return_annotation is str
    assert str(_params("normalize_phone")) == "(text: str, country_code: str) -> str"

    assert _params("strip_accents").return_annotation is str
    assert str(_params("strip_accents")) == "(text: str) -> str"

    assert _params("mask_secret").return_annotation is str
    assert _params("mask_secret").parameters["keep"].default == 4
    assert str(_params("mask_secret")) == "(text: str, keep: int = 4) -> str"

    assert _params("slugify").return_annotation is str
    assert str(_params("slugify")) == "(text: str) -> str"

    assert _params("clamp").return_annotation == float | int
    assert (
        str(_params("clamp"))
        == "(value: float | int, low: float | int, high: float | int) -> float | int"
    )
