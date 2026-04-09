"""
AttackMyLure – Fake HTTP honeypot service.

Presents a convincing router / admin login page.  All POST submissions
(credentials) are logged and the user is shown a generic "wrong password"
error so that attackers keep trying.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import config
import logger as hplog

# ---------------------------------------------------------------------------
# Login page HTML
# ---------------------------------------------------------------------------

_LOGIN_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f0f0f0; display: flex;
            justify-content: center; align-items: center; height: 100vh; margin: 0; }}
    .box {{ background: #fff; padding: 30px 40px; border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,.2); width: 320px; }}
    h2   {{ margin-top: 0; color: #333; }}
    input {{ width: 100%; padding: 8px; margin: 8px 0 16px; box-sizing: border-box;
             border: 1px solid #ccc; border-radius: 4px; }}
    button {{ width: 100%; padding: 10px; background: #0066cc; color: #fff;
              border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }}
    .err {{ color: red; font-size: 13px; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <div class="box">
    <h2>{title}</h2>
    {error}
    <form method="post" action="/login">
      <label>Username</label>
      <input type="text" name="username" autofocus/>
      <label>Password</label>
      <input type="password" name="password"/>
      <button type="submit">Login</button>
    </form>
  </div>
</body>
</html>
"""

_ERROR_BLOCK = '<p class="err">Invalid username or password.</p>'


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class _HoneypotHTTPHandler(BaseHTTPRequestHandler):
    """Serve a fake login page and harvest submitted credentials."""

    # Suppress default request logging to avoid duplicate output
    def log_message(self, fmt: str, *args) -> None:  # type: ignore[override]
        pass

    def _send_page(self, code: int, body: str) -> None:
        encoded = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    # --- GET ---------------------------------------------------------------

    def do_GET(self) -> None:
        src_ip, src_port = self.client_address
        path = urlparse(self.path).path
        hplog.log_attempt("HTTP", src_ip, src_port, extra={"method": "GET", "path": path})
        self._send_page(200, _LOGIN_PAGE.format(title=config.HTTP_TITLE, error=""))

    # --- POST --------------------------------------------------------------

    def do_POST(self) -> None:
        src_ip, src_port = self.client_address
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode(errors="replace")
        params = parse_qs(body)

        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]

        hplog.log_attempt(
            "HTTP",
            src_ip,
            src_port,
            username=username,
            password=password,
            extra={"method": "POST", "path": urlparse(self.path).path},
        )

        # Always return "wrong password" so attackers keep submitting
        self._send_page(
            200,
            _LOGIN_PAGE.format(title=config.HTTP_TITLE, error=_ERROR_BLOCK),
        )


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the HTTP honeypot service (blocking – run in a thread)."""

    server = HTTPServer((config.HTTP_HOST, config.HTTP_PORT), _HoneypotHTTPHandler)
    hplog.logger.info(
        "HTTP honeypot listening on %s:%d", config.HTTP_HOST, config.HTTP_PORT
    )
    server.serve_forever()
