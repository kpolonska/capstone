"""Shared HTTP helpers."""

import json
from http.server import BaseHTTPRequestHandler


class Base(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        return  # keep the journal quiet; the request count is in /health

    def reply(self, status, body=b"", ctype="application/octet-stream", head=False):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head and body:
            self.wfile.write(body)

    def reply_json(self, status, obj, head=False):
        self.reply(status, json.dumps(obj).encode(), "application/json", head)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""
