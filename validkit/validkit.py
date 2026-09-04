"""Pure validation and normalization helpers for validkit."""


def is_valid_email(text: str) -> bool:
    raise NotImplementedError


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
