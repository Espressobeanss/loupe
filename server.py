"""Loupe dev server — Python stdlib only, no dependencies.

Serves the web UI from web/ and exposes the engine at GET /api/report.
Run: python3 server.py   (PORT env var overrides the default 4317)
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from engine.report import build_report

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
PORT = int(os.environ.get("PORT", "4317"))

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/api/report":
            q = parse_qs(url.query)
            role = q.get("role", ["product"])[0]
            depth = q.get("depth", ["standard"])[0]
            body = json.dumps(build_report(role, depth)).encode("utf-8")
            return self._send(200, body, CONTENT_TYPES[".json"])

        path = "/index.html" if url.path in ("", "/") else url.path
        target = os.path.normpath(os.path.join(WEB, path.lstrip("/")))
        if not target.startswith(WEB) or not os.path.isfile(target):
            return self._send(404, b"not found", "text/plain; charset=utf-8")

        ext = os.path.splitext(target)[1]
        with open(target, "rb") as f:
            data = f.read()
        self._send(200, data, CONTENT_TYPES.get(ext, "application/octet-stream"))

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print("Loupe dev server -> http://localhost:%d" % PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
