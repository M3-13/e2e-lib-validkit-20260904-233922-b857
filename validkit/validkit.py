"""Pure validation and normalization helpers for validkit."""

import re

# A single, linear expression: three `+` quantifiers over character classes with a
# literal ``@`` and ``.`` as separators, and no nested quantifiers. This makes
# backtracking O(n) at worst, so no catastrophic ReDoS is possible.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+$")

# A single, linear expression: two fixed-length classes (country code, check
# digits) followed by one bounded quantifier over a character class, and no
# nested quantifiers. Backtracking is O(n) at worst, so no catastrophic ReDoS
# is possible. It also enforces the ISO 13616 length bounds (15..34 characters).
_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$")

# ISO 13616 registry: country code -> expected total IBAN length. The
# country-specific length is part of what makes an IBAN valid, independent of
# its check sum, so a country that is missing here (or a length that does not
# match its entry) is rejected.
_IBAN_LENGTHS = {
    "AD": 24,
    "AE": 23,
    "AL": 28,
    "AT": 20,
    "AZ": 28,
    "BA": 20,
    "BE": 16,
    "BG": 22,
    "BH": 22,
    "BI": 27,
    "BR": 29,
    "BY": 28,
    "CH": 21,
    "CR": 22,
    "CY": 28,
    "CZ": 24,
    "DE": 22,
    "DK": 18,
    "DO": 28,
    "EE": 20,
    "EG": 29,
    "ES": 24,
    "FI": 18,
    "FO": 18,
    "FR": 27,
    "GB": 22,
    "GE": 22,
    "GI": 23,
    "GL": 18,
    "GR": 27,
    "GT": 28,
    "HR": 21,
    "HU": 28,
    "IE": 22,
    "IL": 23,
    "IQ": 23,
    "IS": 26,
    "IT": 27,
    "JO": 30,
    "KW": 30,
    "KZ": 20,
    "LB": 28,
    "LC": 32,
    "LI": 21,
    "LT": 20,
    "LU": 20,
    "LV": 21,
    "LY": 25,
    "MC": 27,
    "MD": 24,
    "ME": 22,
    "MK": 19,
    "MR": 27,
    "MT": 31,
    "MU": 30,
    "NL": 18,
    "NO": 15,
    "PK": 24,
    "PL": 28,
    "PS": 29,
    "PT": 25,
    "QA": 29,
    "RO": 24,
    "RS": 22,
    "SA": 24,
    "SC": 31,
    "SE": 24,
    "SI": 19,
    "SK": 24,
    "SM": 27,
    "ST": 25,
    "SV": 28,
    "TL": 23,
    "TN": 24,
    "TR": 26,
    "UA": 29,
    "VA": 22,
    "VG": 24,
    "XK": 20,
}


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
    97. The input must be an upper-case IBAN of the country-specific length for
    its two-letter country code; an invalid length, an invalid character or a
    wrong check sum returns ``False``. Raises ``TypeError`` for a non-``str``
    input.
    """
    if not isinstance(text, str):
        raise TypeError(f"is_valid_iban() expects a str, got {type(text).__name__}")
    compact = text.replace(" ", "")
    if _IBAN_RE.match(compact) is None:
        return False
    expected_length = _IBAN_LENGTHS.get(compact[:2])
    if expected_length is None or len(compact) != expected_length:
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
    return int(digits) % 97 == 1


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
