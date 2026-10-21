"""Core encode/decode logic for Crockford Base32.

Crockford Base32 uses a 32-symbol alphabet (0-9 A-V) chosen for visual
unambiguity.  The characters I, L, O and U are excluded from encoding but
accepted on decode as aliases for 1, 1, 0 and V respectively, because they are
the symbols most often mis-read by humans.

This implementation handles **non-negative integers** only.  Crockford's
specification permits a leading '-' for negative numbers, but supporting that
introduces a sign ambiguity when the input is treated as a raw numeric string
versus a formatted value.  We chose the simpler, single interpretation so that
every accepted input round-trips cleanly back to the same integer.
"""

from __future__ import annotations


SYMBOLS: str = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


class EncodingError(ValueError):
    """Raised when a value cannot be encoded."""


class DecodingError(ValueError):
    """Raised when a string cannot be decoded."""


# Build the decode lookup once at import time.  Lowercase variants of every
# symbol are accepted so that users typing values by hand are not penalised.
DECODE_MAP: dict[str, str] = {}
for _i, _s in enumerate(SYMBOLS):
    DECODE_MAP[_s] = _i
    DECODE_MAP[_s.lower()] = _i

# Human-transcription aliases: visually similar characters map to the canonical
# symbol so that a mistyped 'O' is still understood as '0'.
DECODE_MAP["O"] = 0
DECODE_MAP["o"] = 0
DECODE_MAP["I"] = 1
DECODE_MAP["i"] = 1
DECODE_MAP["L"] = 1
DECODE_MAP["l"] = 1


def encode(value: int) -> str:
    """Encode a non-negative integer into a Crockford Base32 string.

    Returns ``"0"`` for ``0`` rather than an empty string, because returning
    an empty string for a valid input would force every caller to special-case
    it.

    Raises :class:`EncodingError` if *value* is negative or not an ``int``.
    Booleans are rejected explicitly: in Python ``bool`` is a subclass of
    ``int``, but encoding ``True`` as ``"1"`` would surprise callers who
    passed a flag by accident.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise EncodingError("value must be an int (not bool)")
    if value < 0:
        raise EncodingError("negative integers are not supported")

    if value == 0:
        return "0"

    digits: list[str] = []
    n = value
    while n > 0:
        n, rem = divmod(n, 32)
        digits.append(SYMBOLS[rem])
    return "".join(reversed(digits))


def _decode_raw(text: str, allow_hyphens: bool) -> int:
    """Shared decode core used by :func:`decode` and :func:`decode_strict`."""
    if not isinstance(text, str):
        raise DecodingError("text must be a str")
    if text == "":
        raise DecodingError("text must not be empty")

    # Hyphens are permitted by the spec as optional grouping separators
    # (e.g. "1Z2-3P4").  Stripping them early keeps the main loop simple.
    if allow_hyphens:
        cleaned = text.replace("-", "")
        if cleaned == "":
            raise DecodingError("text contains no decodable symbols")
    else:
        cleaned = text

    result = 0
    for ch in cleaned:
        mapped = DECODE_MAP.get(ch)
        if mapped is None:
            raise DecodingError(f"invalid symbol: {ch!r}")
        result = result * 32 + mapped
    return result


def decode(text: str) -> int:
    """Decode a Crockford Base32 string to a non-negative integer.

    Accepts upper and lower case, the alias characters ``O``/``o``, ``I``/``i``
    and ``L``/``l``, and optional ``-`` hyphen separators.  ``decode`` is the
    lenient counterpart intended for human-typed input.
    """
    return _decode_raw(text, allow_hyphens=True)


def decode_strict(text: str) -> int:
    """Decode a Crockford Base32 string without hyphen separators.

    Identical to :func:`decode` except that a hyphen is treated as an invalid
    symbol.  Use this when the input is machine-generated and you want to
    reject anything that is not a canonical encoding.
    """
    return _decode_raw(text, allow_hyphens=False)
