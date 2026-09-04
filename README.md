# validkit

validkit ist eine kleine, eigenständige Python-Bibliothek mit neun unabhängigen,
reinen und typannotierten Prüf- und Normalisierungsfunktionen: `is_valid_email`,
`luhn_check`, `is_valid_iban`, `is_valid_isbn13`, `normalize_phone`,
`strip_accents`, `mask_secret`, `slugify` und `clamp`.

Jede Funktion ist einzeln nutzbar, meldet ungültige Eingaben mit einem
aussagekräftigen Fehler (`TypeError` bei falschem Typ, `ValueError` bei
semantisch ungültigen Werten) und wird über `validkit/__init__.py` exportiert,
sodass `from validkit import ...` direkt funktioniert.

## Tech-Stack

- **Sprache**: Python 3.10+
- **Abhängigkeiten**: keine – ausschließlich Standardbibliothek
  (`re`, `unicodedata`, `string`, `math`)
- **Tests**: pytest

## Installation

Da validkit keine Laufzeit-Abhängigkeiten besitzt, genügt eine Installation in
editierbarem Modus:

```bash
pip install -e .
```

Alternativ funktioniert auch ein direkter Import aus dem Repository-Root ohne
Installation, da das Paket als `validkit/`-Verzeichnis neben den Tests liegt.

## Tests ausführen

```bash
pip install -e ".[test]"   # installiert pytest als optionale Test-Abhängigkeit
pytest
```

## Verwendung

Alle neun Funktionen sind aus dem Paket importierbar:

```python
from validkit import is_valid_email, luhn_check, is_valid_iban, is_valid_isbn13
from validkit import normalize_phone, strip_accents, mask_secret, slugify, clamp
```

### is_valid_email

```python
from validkit import is_valid_email

is_valid_email("alice@example.com")  # True
is_valid_email("alice@")  # False
is_valid_email("@example.com")  # False
is_valid_email("aliceexample.com")  # False
is_valid_email("")  # False
```

### luhn_check

```python
from validkit import luhn_check

luhn_check(79927398713)  # True
luhn_check(79927398712)  # False
luhn_check("")  # False
```

### is_valid_iban

```python
from validkit import is_valid_iban

is_valid_iban("DE89 3704 0044 0532 0130 00")  # True
is_valid_iban("DE89 3704 0044 0532 0130 01")  # False (eine Ziffer verändert)
is_valid_iban("")  # False
```

### is_valid_isbn13

```python
from validkit import is_valid_isbn13

is_valid_isbn13("978-3-16-148410-0")  # True
is_valid_isbn13("978-3-16-148410-1")  # False (falsche Prüfziffer)
is_valid_isbn13("978316148410")  # False (nur 12 Ziffern)
is_valid_isbn13("978-3-16-14841x-0")  # False (Nicht-Ziffern)
```

### normalize_phone

```python
from validkit import normalize_phone

normalize_phone("030 1234567", "49")  # "+49301234567"
normalize_phone("+49301234567", "49")  # "+49301234567" (keine doppelte Vorwahl)
```

### strip_accents

```python
from validkit import strip_accents

strip_accents("München café naïve")  # "Munchen cafe naive"
```

### mask_secret

```python
from validkit import mask_secret

mask_secret("geheim123", keep=4)  # "*****m123"
```

### slugify

```python
from validkit import slugify

slugify("Héllo Wörld! -- Foo_ Bar")  # "hello-world-foo-bar"
```

### clamp

```python
from validkit import clamp

clamp(5, 0, 10)  # 5
clamp(-3, 0, 10)  # 0
clamp(15, 0, 10)  # 10
clamp(2.5, 1, 3)  # 2.5
```
