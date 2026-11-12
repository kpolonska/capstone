"""Consistent-hash ring with virtual nodes (see ADR-005)."""

import bisect

from .xxh64 import xxh64

VNODES_PER_SHARD = 100


class Ring:
    def __init__(self, vnodes=VNODES_PER_SHARD):
        self.vnodes = vnodes
        self._points = []   # sorted hash positions
        self._owners = []   # shard id at each position, same order as _points
        self._shards = set()

    def add(self, shard_id):
        if shard_id in self._shards:
            return
        self._shards.add(shard_id)
        for i in range(self.vnodes):
            point = xxh64(f"{shard_id}#{i}".encode())
            idx = bisect.bisect_left(self._points, point)
            self._points.insert(idx, point)
            self._owners.insert(idx, shard_id)

    def shards(self):
        return sorted(self._shards)

    def lookup(self, key):
        """Return the shard id that owns `key` (bytes): first point clockwise, wrapping."""
        if not self._points:
            raise LookupError("ring has no shards")
        idx = bisect.bisect_left(self._points, xxh64(key))
        if idx == len(self._points):
            idx = 0
        return self._owners[idx]
