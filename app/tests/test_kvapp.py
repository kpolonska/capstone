import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from kvapp.coordinator import make_handler as coord_handler
from kvapp.ring import Ring
from kvapp.shard import ShardState, make_handler as shard_handler
from kvapp.xxh64 import xxh64


def start(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def call(method, url, body=None):
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


class Xxh64Test(unittest.TestCase):
    def test_reference_vectors(self):
        self.assertEqual(xxh64(b""), 0xEF46DB3751D8E999)
        self.assertEqual(xxh64(b"abc"), 0x44BC2CF5AD770999)

    def test_long_input_is_deterministic(self):
        data = bytes(range(256)) * 3
        self.assertEqual(xxh64(data), xxh64(data))
        self.assertNotEqual(xxh64(data), xxh64(data[:-1]))


class RingTest(unittest.TestCase):
    def test_two_shards_split_100k_keys_near_half(self):
        ring = Ring()
        ring.add("a")
        ring.add("b")
        count_a = sum(ring.lookup(f"t/key{i}".encode()) == "a" for i in range(100_000))
        share = count_a / 100_000
        self.assertTrue(0.40 <= share <= 0.60, f"shard a share was {share:.3f}")

    def test_adding_a_shard_moves_only_some_keys(self):
        ring = Ring()
        ring.add("a")
        ring.add("b")
        before = {i: ring.lookup(f"t/k{i}".encode()) for i in range(10_000)}
        ring.add("c")
        moved = sum(before[i] != ring.lookup(f"t/k{i}".encode()) for i in range(10_000))
        self.assertLess(moved / 10_000, 0.5)


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.states = [ShardState(), ShardState()]
        self.shards = [start(shard_handler(s)) for s in self.states]
        ring, shards, tables, lock = Ring(), {}, set(), threading.Lock()
        self.coord, self.url = start(coord_handler(ring, shards, tables, lock))
        for sid, (_, surl) in zip("ab", self.shards):
            status, _ = call("POST", f"{self.url}/shards", b'{"id": "%s", "url": "%s"}' % (sid.encode(), surl.encode()))
            self.assertEqual(status, 201)

    def tearDown(self):
        for server in [self.coord, *[s[0] for s in self.shards]]:
            server.shutdown()
            server.server_close()

    def test_crud_through_coordinator(self):
        self.assertEqual(call("PUT", f"{self.url}/tables/users")[0], 200)
        base = f"{self.url}/tables/users/items/alice"
        self.assertEqual(call("PUT", base, b"hello")[0], 200)
        self.assertEqual(call("GET", base), (200, b"hello"))
        self.assertEqual(call("HEAD", base)[0], 200)
        self.assertEqual(call("DELETE", base)[0], 200)
        self.assertEqual(call("GET", base)[0], 404)

    def test_missing_table_is_rejected(self):
        self.assertEqual(call("PUT", f"{self.url}/tables/nope/items/x", b"v")[0], 404)

    def test_items_spread_across_both_shards(self):
        call("PUT", f"{self.url}/tables/t")
        for i in range(200):
            call("PUT", f"{self.url}/tables/t/items/k{i}", b"v")
        counts = [len(state.items) for state in self.states]
        self.assertEqual(sum(counts), 200)
        self.assertTrue(all(c > 0 for c in counts), counts)


if __name__ == "__main__":
    unittest.main()
