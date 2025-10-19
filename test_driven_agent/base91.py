"""BasE91 encoding and decoding functions."""

def b91encode(data: str) -> str:
    """Encode a string to BasE91.
    
    Args:
        data: The input string to encode.
    
    Returns:
        The encoded BasE91 string.
    """
    # Base91 algorithm implementation
    b = 0
    n = 0
    out = []
    for byte in bytearray(data, 'utf-8'):
        b |= byte << n
        n += 8
        if n > 13:
            v = b & 8191
            if v > 88:
                b >>= 13
                n -= 13
            else:
                v = b & 16383
                b >>= 14
                n -= 14
            out.append('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#'
                      '$%&()*+,./:;<=>?@[]^_`{|}~"'[v % 91])
            out.append('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#'
                      '$%&()*+,./:;<=>?@[]^_`{|}~"'[v // 91])
    if n > 0:
        out.append('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#'
                  '$%&()*+,./:;<=>?@[]^_`{|}~"'[b % 91])
        if n > 7 or b > 90:
            out.append('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#'
                      '$%&()*+,./:;<=>?@[]^_`{|}~"'[b // 91])
    return ''.join(out)


def b91decode(data: str) -> str:
    """Decode a BasE91 string.
    
    Args:
        data: The encoded BasE91 string.
    
    Returns:
        The decoded string.
    """
    # Base91 algorithm implementation
    b = 0
    n = 0
    out = []
    v = -1
    base91_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#' \
                   '$%&()*+,./:;<=>?@[]^_`{|}~"'
    for c in data:
        if c not in base91_chars:
            continue
        p = base91_chars.index(c)
        if v < 0:
            v = p
        else:
            v += p * 91
            b |= v << n
            n += 13 if (v & 8191) > 88 else 14
            while n > 7:
                out.append((b & 255).to_bytes(1, 'little').decode('latin-1'))
                b >>= 8
                n -= 8
            v = -1
    if v + 1:
        b |= (v & 16383) << n
        out.append(b.to_bytes((n + 7) // 8, 'little').decode('latin-1'))
    return ''.join(out)


if __name__ == "__main__":
    import unittest

    class TestBase91(unittest.TestCase):
        """Test cases for BasE91 encoding and decoding."""

        def test_encode_decode(self):
            """Test encoding and decoding round-trip."""
            test_cases = [
                ("test", "fPNKd"),
                ("Hello World!", ">OwJh>Io0Tv!8PE"),
            ]
            for plain, encoded in test_cases:
                with self.subTest(plain=plain, encoded=encoded):
                    self.assertEqual(b91encode(plain), encoded)
                    self.assertEqual(b91decode(encoded), plain)

    unittest.main()
