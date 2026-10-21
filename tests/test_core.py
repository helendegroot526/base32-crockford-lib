import unittest

from base32_crockford_lib import (
    encode,
    decode,
    decode_strict,
    EncodingError,
    DecodingError,
)


class TestEncode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode(0), "0")

    def test_simple_values(self):
        self.assertEqual(encode(1), "1")
        self.assertEqual(encode(31), "Z")
        self.assertEqual(encode(32), "10")

    def test_known_vector(self):
        # 1234567 in base 32 -> 15NM7
        self.assertEqual(encode(1234567), "15NM7")

    def test_roundtrip_large(self):
        n = 2 ** 63 - 1
        self.assertEqual(decode(encode(n)), n)

    def test_rejects_negative(self):
        with self.assertRaises(EncodingError):
            encode(-1)

    def test_rejects_bool(self):
        with self.assertRaises(EncodingError):
            encode(True)
        with self.assertRaises(EncodingError):
            encode(False)

    def test_rejects_non_int(self):
        with self.assertRaises(EncodingError):
            encode("16")  # type: ignore[arg-type]
        with self.assertRaises(EncodingError):
            encode(1.5)  # type: ignore[arg-type]


class TestDecode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(decode("0"), 0)

    def test_lowercase(self):
        self.assertEqual(decode("15nm7"), 1234567)

    def test_alias_o(self):
        self.assertEqual(decode("O"), 0)
        self.assertEqual(decode("o"), 0)

    def test_alias_i_and_l(self):
        self.assertEqual(decode("I"), 1)
        self.assertEqual(decode("i"), 1)
        self.assertEqual(decode("L"), 1)
        self.assertEqual(decode("l"), 1)

    def test_hyphens_allowed(self):
        self.assertEqual(decode("1Z2-3P4"), decode("1Z23P4"))

    def test_invalid_symbol(self):
        with self.assertRaises(DecodingError):
            decode("!")

    def test_empty_string(self):
        with self.assertRaises(DecodingError):
            decode("")

    def test_non_string(self):
        with self.assertRaises(DecodingError):
            decode(123)  # type: ignore[arg-type]

    def test_hyphens_only(self):
        with self.assertRaises(DecodingError):
            decode("---")


class TestDecodeStrict(unittest.TestCase):
    def test_rejects_hyphen(self):
        with self.assertRaises(DecodingError):
            decode_strict("1-2")

    def test_accepts_clean(self):
        self.assertEqual(decode_strict("15NM7"), 1234567)

    def test_alias_still_accepted(self):
        self.assertEqual(decode_strict("O"), 0)


if __name__ == "__main__":
    unittest.main()
