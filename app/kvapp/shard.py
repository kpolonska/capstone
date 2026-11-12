"""Shard server: stores items in memory. Internal API on port 8081 (see ADR-004, ADR-006)."""

import threading
from http.server import ThreadingHTTPServer
from urllib.parse import unquote

from .common import Base

PORT = 8081


class ShardState:
    def __init__(self):
        self.items = {}
        self.lock = threading.Lock()


def make_handler(state):
    class ShardHandler(Base):
        def _key(self):
            # Internal path: /data/<url-encoded partition key>
            if not self.path.startswith("/data/"):
                return None
            return unquote(self.path[len("/data/"):])

        def _route(self, head=False):
            if self.path == "/health":
                with state.lock:
                    return self.reply_json(200, {"items": len(state.items)}, head)
            key = self._key()
            if key is None:
                return self.reply_json(404, {"error": "not found"}, head)
            if self.command == "PUT":
                body = self.read_body()
                with state.lock:
                    state.items[key] = body
                return self.reply(200, b"", head=head)
            with state.lock:
                value = state.items.get(key)
            if value is None:
                return self.reply_json(404, {"error": "no such item"}, head)
            if self.command == "DELETE":
                with state.lock:
                    state.items.pop(key, None)
                return self.reply(200, b"", head=head)
            return self.reply(200, value, head=head)  # GET and HEAD

        def do_GET(self):
            self._route()

        def do_HEAD(self):
            self._route(head=True)

        def do_PUT(self):
            self._route()

        def do_DELETE(self):
            self._route()

    return ShardHandler


def serve(port=PORT):
    server = ThreadingHTTPServer(("0.0.0.0", port), make_handler(ShardState()))
    server.serve_forever()
