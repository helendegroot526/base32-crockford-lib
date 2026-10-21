# base32-crockford-lib

Encodes and decodes non-negative integers using Douglas Crockford's Base32 variant, which was designed for reliable human transcription.

```python
from base32_crockford_lib import encode, decode, decode_strict, DecodingError

assert encode(1234567) == "15NM7"
assert decode("15NM7") == 1234567
assert decode("15nm7") == 1234567      # lower case accepted
assert decode("1Z2-3P4") == decode("1Z23P4")  # hyphens ignored
try:
    decode_strict("1-2")  # raises DecodingError
except DecodingError:
    pass
```

Exported names: `encode`, `decode`, `decode_strict`, `EncodingError`, `DecodingError`, `SYMBOLS`, `DECODE_MAP`.

## Why this exists

When a short identifier has to be read by a human and typed back in — a license key, a confirmation code, a serial number — the symbols 0/O and 1/I/L are the ones that get confused most often. Crockford Base32 drops U (to avoid accidental profanity) and remaps the visually ambiguous characters so that a mistyped `O` still decodes as `0`. This library gives you that alphabet with no dependencies.

The trade-off: this library handles **non-negative integers only**. Crockford's specification allows a leading `-` for negatives, but supporting that introduces ambiguity between a formatted sign and a grouping hyphen, so we chose the single, clean interpretation.

## Edge cases worth knowing

- `encode(0)` returns `"0"`, not an empty string.
- `bool` values are rejected by `encode` even though `bool` subclasses `int`, because silently encoding `True` as `"1"` would mask logic errors in calling code.
- `decode` accepts hyphens as optional separators; `decode_strict` does not. Use `decode_strict` when the input is machine-generated and you want to reject anything non-canonical.

Run the tests with:

```
PYTHONPATH=src python -m unittest discover -s tests
```
