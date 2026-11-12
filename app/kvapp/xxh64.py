"""Pure-Python xxHash64 (a fast, non-cryptographic 64-bit hash).

Pure Python is used because the shard servers cannot pip-install the C-extension
`xxhash` package. Output matches the reference XXH64 algorithm (seed 0 by default).
"""

M64 = (1 << 64) - 1
P1 = 0x9E3779B185EBCA87
P2 = 0xC2B2AE3D27D4EB4F
P3 = 0x165667B19E3779F9
P4 = 0x85EBCA77C2B2AE63
P5 = 0x27D4EB2F165667C5


def _rotl(x, r):
    return ((x << r) | (x >> (64 - r))) & M64


def _round(acc, lane):
    acc = (acc + lane * P2) & M64
    acc = _rotl(acc, 31)
    return (acc * P1) & M64


def _merge(acc, val):
    acc ^= _round(0, val)
    return (acc * P1 + P4) & M64


def xxh64(data, seed=0):
    """Return the 64-bit xxHash of `data` (bytes) as an int."""
    n = len(data)
    p = 0
    if n >= 32:
        v1 = (seed + P1 + P2) & M64
        v2 = (seed + P2) & M64
        v3 = seed & M64
        v4 = (seed - P1) & M64
        while p <= n - 32:
            v1 = _round(v1, int.from_bytes(data[p:p + 8], "little")); p += 8
            v2 = _round(v2, int.from_bytes(data[p:p + 8], "little")); p += 8
            v3 = _round(v3, int.from_bytes(data[p:p + 8], "little")); p += 8
            v4 = _round(v4, int.from_bytes(data[p:p + 8], "little")); p += 8
        h = (_rotl(v1, 1) + _rotl(v2, 7) + _rotl(v3, 12) + _rotl(v4, 18)) & M64
        h = _merge(h, v1)
        h = _merge(h, v2)
        h = _merge(h, v3)
        h = _merge(h, v4)
    else:
        h = (seed + P5) & M64
    h = (h + n) & M64
    while p + 8 <= n:
        h ^= _round(0, int.from_bytes(data[p:p + 8], "little"))
        h = (_rotl(h, 27) * P1 + P4) & M64
        p += 8
    if p + 4 <= n:
        h ^= (int.from_bytes(data[p:p + 4], "little") * P1) & M64
        h = (_rotl(h, 23) * P2 + P3) & M64
        p += 4
    while p < n:
        h ^= (data[p] * P5) & M64
        h = (_rotl(h, 11) * P1) & M64
        p += 1
    h ^= h >> 33
    h = (h * P2) & M64
    h ^= h >> 29
    h = (h * P3) & M64
    h ^= h >> 32
    return h
