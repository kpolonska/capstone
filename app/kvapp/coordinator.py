"""Coordinator: public REST API on port 8080. Routes keys to shards via the ring (ADR-004, ADR-005, ADR-006)."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from urllib.parse import quote, unquote

from .common import Base
from .ring import Ring

PORT = 8080
SHARD_TIMEOUT = 3


def make_handler(ring, shards, tables, lock):
    class CoordinatorHandler(Base):
        def _forward(self, shard_url, pkey, method, body=None):
            req = urllib.request.Request(
                f"{shard_url}/data/{quote(pkey, safe='')}", data=body, method=method)
            try:
                with urllib.request.urlopen(req, timeout=SHARD_TIMEOUT) as r:
                    return r.status, r.read() if method == "GET" else b""
            except urllib.error.HTTPError as e:
                return e.code, b""
            except (urllib.error.URLError, OSError):
                return 503, b""

        def _route(self, head=False):
            path = self.path.split("?", 1)[0]
            parts = path.split("/", 4)  # ['', 'tables', table, 'items', key]
            if self.command == "GET" and path == "/health":
                return self.reply_json(200, {"shards": ring.shards(), "tables": len(tables)}, head)
            if len(parts) >= 3 and parts[1] == "tables" and len(parts) == 3:
                table = unquote(parts[2])
                if self.command == "PUT":
                    with lock:
                        tables.add(table)
                    return self.reply_json(200, {"table": table}, head)
            if len(parts) == 5 and parts[1] == "tables" and parts[3] == "items":
                table, key = unquote(parts[2]), unquote(parts[4])
                with lock:
                    exists = table in tables
                if not exists:
                    return self.reply_json(404, {"error": "no such table"}, head)
                pkey = f"{table}/{key}"  # partition key per ADR-006
                try:
                    with lock:
                        shard_id = ring.lookup(pkey.encode())
                        shard_url = shards[shard_id]
                except LookupError:
                    return self.reply_json(503, {"error": "no shards registered"}, head)
                body = self.read_body() if self.command == "PUT" else None
                method = self.command
                status, data = self._forward(shard_url, pkey, method, body)
                if status == 503:
                    return self.reply_json(503, {"error": f"shard {shard_id} unreachable"}, head)
                if method == "GET" and status == 200:
                    return self.reply(200, data, head=head)
                if method == "HEAD" or method == "DELETE" or method == "PUT":
                    return self.reply(status, b"", head=head)
                return self.reply_json(status, {"error": "no such item"}, head)
            return self.reply_json(404, {"error": "not found"}, head)

        def do_GET(self):
            if self.path == "/shards":
                with lock:
                    return self.reply_json(200, {"shards": {k: v for k, v in shards.items()}})
            self._route()

        def do_HEAD(self):
            self._route(head=True)

        def do_PUT(self):
            self._route()

        def do_DELETE(self):
            self._route()

        def do_POST(self):
            # Shard registration (M2 task 3): POST /shards {"id": "a", "url": "http://10.0.10.202:8081"}
            if self.path != "/shards":
                return self.reply_json(404, {"error": "not found"})
            try:
                info = json.loads(self.read_body() or b"{}")
                shard_id, url = str(info["id"]), str(info["url"]).rstrip("/")
            except (ValueError, KeyError):
                return self.reply_json(400, {"error": "expected JSON with id and url"})
            with lock:
                shards[shard_id] = url
                ring.add(shard_id)
            return self.reply_json(201, {"id": shard_id, "url": url})

    return CoordinatorHandler


def serve(port=PORT):
    ring, shards, tables, lock = Ring(), {}, set(), threading.Lock()
    server = ThreadingHTTPServer(("0.0.0.0", port), make_handler(ring, shards, tables, lock))
    server.serve_forever()
