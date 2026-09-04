"""Pure validation and normalization helpers for validkit."""

import re
import unicodedata

# A single, linear expression: three `+` quantifiers over character classes with a
# literal ``@`` and ``.`` as separators, and no nested quantifiers. This makes
# backtracking O(n) at worst, so no catastrophic ReDoS is possible.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+$")

# A single, linear expression: two fixed-length classes (country code, check
# digits) followed by one bounded quantifier over a character class, and no
# nested quantifiers. Backtracking is O(n) at worst, so no catastrophic ReDoS
# is possible. It also enforces the ISO 13616 length bounds (15..34 characters).
_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$")

# Exactly thirteen digits, nothing else. The quantifier is a single fixed
# count ({13}) with no nested quantifiers, so backtracking is O(1) once a
# character fails and no catastrophic ReDoS is possible. ``\Z`` (unlike ``$``)
# anchors to the true end of the string, so a trailing newline is rejected.
_ISBN13_RE = re.compile(r"^[0-9]{13}\Z")


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
    """Return True if *digits* passes the Luhn checksum algorithm.

    *digits* may be an ``int`` or a ``str``. A string may contain only digits,
    optionally separated by spaces or hyphens, which are ignored. An empty or
    otherwise non-numeric input returns ``False``. Raises ``TypeError`` for any
    type other than ``str`` or ``int``.
    """
    if isinstance(digits, bool) or not isinstance(digits, (str, int)):
        raise TypeError(f"luhn_check() expects a str or int, got {type(digits).__name__}")
    if isinstance(digits, int):
        if digits < 0:
            return False
        digits = str(digits)

    cleaned = digits.replace(" ", "").replace("-", "")
    if not cleaned or not cleaned.isdigit():
        return False

    total = 0
    for index, char in enumerate(reversed(cleaned)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def is_valid_iban(text: str) -> bool:
    """Return True if *text* is a structurally and mathematically valid IBAN.

    The check follows ISO 13616 / ISO 7064 (MOD 97-10): spaces are ignored, the
    first four characters are moved to the end, letters are replaced by A=10 ..
    Z=35 and the resulting number must leave a remainder of 1 when divided by
    97. The input must be an upper-case IBAN of 15 to 34 characters; an invalid
    length, an invalid character or a wrong check sum returns ``False``. Raises
    ``TypeError`` for a non-``str`` input.
    """
    if not isinstance(text, str):
        raise TypeError(f"is_valid_iban() expects a str, got {type(text).__name__}")
    compact = text.replace(" ", "")
    if _IBAN_RE.match(compact) is None:
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
    return int(digits) % 97 == 1


def is_valid_isbn13(text: str) -> bool:
    """Return True if *text* is a valid ISBN-13 number.

    Hyphens and spaces are tolerated and ignored, so both ``978-3-16-148410-0``
    and ``9783161484100`` validate. The input must contain exactly thirteen
    digits; the final one is the check digit, computed from the first twelve
    with the alternating 1/3 weighting scheme. A wrong length, an invalid
    character or a wrong check digit returns ``False``. Raises ``TypeError``
    for a non-``str`` input.
    """
    if not isinstance(text, str):
        raise TypeError(f"is_valid_isbn13() expects a str, got {type(text).__name__}")
    compact = text.replace("-", "").replace(" ", "")
    if _ISBN13_RE.match(compact) is None:
        return False
    total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(compact[:12]))
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(compact[12])


def normalize_phone(text: str, country_code: str) -> str:
    """Normalize *text* to an E.164 phone number (``+<country><national>``).

    Non-digit characters (spaces, parentheses, hyphens, dots) are removed. A
    leading ``00`` is treated as the international prefix, an existing ``+`` is
    kept as-is, and a number without either gets *country_code* prepended — so an
    existing country code is never duplicated. The result starts with ``+`` and
    contains 7 to 15 digits; any other length raises ``ValueError``. A non-``str``
    *text* or *country_code* raises ``TypeError``; a missing/empty *country_code*
    raises ``ValueError``. Error messages never contain the input values.
    """
    if not isinstance(text, str):
        raise TypeError(f"normalize_phone() expects a str for text, got {type(text).__name__}")
    if country_code is None:
        raise ValueError("normalize_phone() requires a non-empty country_code")
    if not isinstance(country_code, str):
        raise TypeError(
            f"normalize_phone() expects a str for country_code, got {type(country_code).__name__}"
        )

    country = re.sub(r"\D", "", country_code)
    if not country:
        raise ValueError("normalize_phone() requires a non-empty country_code")

    digits = re.sub(r"\D", "", text)
    has_plus = text.lstrip().startswith("+")
    has_leading_00 = digits.startswith("00")

    if has_leading_00:
        digits = digits[2:]
    elif not has_plus:
        # A national number starts with the trunk prefix "0" (e.g. "030" for
        # Berlin); it is not part of the international number, so drop it before
        # prepending the country code.
        if digits.startswith("0"):
            digits = digits[1:]
        digits = country + digits

    if not 7 <= len(digits) <= 15:
        raise ValueError("normalize_phone() result must have between 7 and 15 digits")

    return "+" + digits


def strip_accents(text: str) -> str:
    """Return *text* with diacritical marks (accents, umlauts) removed.

    The input is decomposed with Unicode NFD normalization, then every character
    of the combining mark category ``Mn`` (nonspacing marks such as acute,
    circumflex and diaeresis) is dropped, leaving the base letters behind:
    ``München café naïve`` becomes ``Munchen cafe naive``. A character without an
    accent is left unchanged, and a base letter that has no decomposition (such
    as ``ß``) is kept as-is. Raises ``TypeError`` for a non-``str`` input.
    """
    if not isinstance(text, str):
        raise TypeError(f"strip_accents() expects a str, got {type(text).__name__}")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def mask_secret(text: str, keep: int = 4) -> str:
    """Return *text* with everything but the last *keep* characters masked.

    The last *keep* characters stay visible and every preceding character is
    replaced by ``*``. A *text* whose length is less than or equal to *keep* is
    masked completely, so ``mask_secret("geheim123", keep=4)`` returns
    ``"*****m123"``. *keep* must be a non-negative ``int``; a negative *keep*
    raises ``ValueError``, a non-``int`` *keep* (or non-``str`` *text*) raises
    ``TypeError``. Error messages never contain the input values.
    """
    if not isinstance(text, str):
        raise TypeError(f"mask_secret() expects a str, got {type(text).__name__}")
    if isinstance(keep, bool) or not isinstance(keep, int):
        raise TypeError(f"mask_secret() expects an int for keep, got {type(keep).__name__}")
    if keep < 0:
        raise ValueError("mask_secret() keep must be a non-negative integer")

    visible = keep if len(text) > keep else 0
    return "*" * (len(text) - visible) + text[len(text) - visible :]


# A single linear expression: one `+` quantifier over a negated character
# class with no nested quantifiers. Backtracking is O(n) at worst, so no
# catastrophic ReDoS is possible.
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Return a URL-safe slug for *text*.

    The input is lowercased, diacritical marks are removed (``Héllo`` becomes
    ``hello``), and every run of characters that is not an ASCII letter or digit
    is replaced by a single hyphen. Repeated hyphens are collapsed and leading
    and trailing hyphens are stripped, so ``"Héllo Wörld! -- Foo_ Bar"`` becomes
    ``"hello-world-foo-bar"``. An input made only of non-alphanumeric characters
    yields ``""``. Raises ``TypeError`` for a non-``str`` input.
    """
    if not isinstance(text, str):
        raise TypeError(f"slugify() expects a str, got {type(text).__name__}")
    decomposed = unicodedata.normalize("NFD", text)
    ascii_text = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    lower = ascii_text.lower()
    replaced = _SLUG_RE.sub("-", lower)
    return replaced.strip("-")


def clamp(value: float | int, low: float | int, high: float | int) -> float | int:
    raise NotImplementedError
