import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / "index.html"
SERVICE_NAME = "bounce-v5-prototype"
VERSION = "v5-l1"


class BounceV5Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "app": "Bounce",
                    "service": "bounce-v5-prototype",
                    "version": VERSION,
                },
            )
            return

        if path in {"", "/", "/index.html"}:
            self._send_html(INDEX_HTML.read_bytes())
            return

        # Keep the single-file prototype resilient to manual deep-link attempts.
        self._send_html(INDEX_HTML.read_bytes())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

    def _send_html(self, body: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: HTTPStatus, payload: dict[str, str]) -> None:
        body = json.dumps(payload, separators=(",", ": ")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), BounceV5Handler)
    print(f"{SERVICE_NAME} listening on 0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
