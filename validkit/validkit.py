"""Pure validation and normalization helpers for validkit."""

import re

# A single, linear expression: three `+` quantifiers over character classes with a
# literal ``@`` and ``.`` as separators, and no nested quantifiers. This makes
# backtracking O(n) at worst, so no catastrophic ReDoS is possible.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+$")


def is_valid_email(text: str) -> bool:
    """Return True if *text* looks like a syntactically plausible e-mail address.

    The address must contain exactly one ``@``, a non-empty local part and a
    domain part with at least one dot and valid characters. The local part allows
    letters, digits and ``. _ % + -``; the domain allows letters, digits, ``.`` and
    ``-``. Raises ``TypeError`` for a non-``str`` input.
    """
    if not isinstance(text, str):
        raise TypeError(f"is_valid_email() expects a str, got {type(text).__name__}")
    return _EMAIL_RE.match(text) is not None


def luhn_check(digits: str | int) -> bool:
    raise NotImplementedError


def is_valid_iban(text: str) -> bool:
    raise NotImplementedError


def is_valid_isbn13(text: str) -> bool:
    raise NotImplementedError


def normalize_phone(text: str, country_code: str) -> str:
    raise NotImplementedError


def strip_accents(text: str) -> str:
    raise NotImplementedError


def mask_secret(text: str, keep: int = 4) -> str:
    raise NotImplementedError


def slugify(text: str) -> str:
    raise NotImplementedError


def clamp(value: float | int, low: float | int, high: float | int) -> float | int:
    raise NotImplementedError
