"""
Tests for AttackMyLure honeypot.

Run with:  python -m pytest tests/ -v
"""

import importlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

# Make sure the project root is importable regardless of CWD
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _free_port() -> int:
    """Return an available TCP port on localhost."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

class TestConfig(unittest.TestCase):
    def test_ports_are_positive_integers(self):
        import config
        for attr in ("SSH_PORT", "HTTP_PORT", "FTP_PORT", "TELNET_PORT"):
            val = getattr(config, attr)
            self.assertIsInstance(val, int, attr)
            self.assertGreater(val, 0, attr)

    def test_hosts_are_strings(self):
        import config
        for attr in ("SSH_HOST", "HTTP_HOST", "FTP_HOST", "TELNET_HOST"):
            self.assertIsInstance(getattr(config, attr), str, attr)

    def test_banners_are_strings(self):
        import config
        self.assertIsInstance(config.SSH_BANNER, str)
        self.assertIsInstance(config.FTP_BANNER, str)
        self.assertIsInstance(config.HTTP_TITLE, str)

    def test_telnet_banner_is_bytes(self):
        import config
        self.assertIsInstance(config.TELNET_BANNER, bytes)

    def test_log_dir_and_file_are_strings(self):
        import config
        self.assertIsInstance(config.LOG_DIR, str)
        self.assertIsInstance(config.LOG_FILE, str)


# ---------------------------------------------------------------------------
# logger
# ---------------------------------------------------------------------------

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Redirect log output to a temp file for each test
        self.log_file = os.path.join(self.tmpdir, "test.log")

    def _call_log_attempt(self, **kwargs):
        """Call log_attempt with a patched LOG_FILE."""
        import config
        import logger as hplog

        with patch.object(config, "LOG_FILE", self.log_file):
            # Re-patch the open call inside logger so it writes to our temp file
            hplog.log_attempt(**kwargs)

        # Read back what was actually written
        if os.path.exists(config.LOG_FILE):
            with open(config.LOG_FILE, encoding="utf-8") as fh:
                return [json.loads(l) for l in fh if l.strip()]
        return []

    def test_log_attempt_writes_json_line(self):
        import config
        import logger as hplog

        with patch.object(config, "LOG_FILE", self.log_file):
            hplog.log_attempt("SSH", "1.2.3.4", 1234, username="admin", password="secret")

        with open(self.log_file, encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip()]

        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["service"], "SSH")
        self.assertEqual(record["src_ip"], "1.2.3.4")
        self.assertEqual(record["src_port"], 1234)
        self.assertEqual(record["username"], "admin")
        self.assertEqual(record["password"], "secret")
        self.assertIn("timestamp", record)

    def test_log_attempt_without_credentials(self):
        import config
        import logger as hplog

        with patch.object(config, "LOG_FILE", self.log_file):
            hplog.log_attempt("FTP", "10.0.0.1", 9999)

        with open(self.log_file, encoding="utf-8") as fh:
            record = json.loads(fh.read().strip())

        self.assertNotIn("username", record)
        self.assertNotIn("password", record)
        self.assertEqual(record["service"], "FTP")

    def test_log_attempt_extra_fields(self):
        import config
        import logger as hplog

        with patch.object(config, "LOG_FILE", self.log_file):
            hplog.log_attempt(
                "HTTP", "192.168.1.1", 80,
                extra={"method": "POST", "path": "/login"}
            )

        with open(self.log_file, encoding="utf-8") as fh:
            record = json.loads(fh.read().strip())

        self.assertEqual(record["method"], "POST")
        self.assertEqual(record["path"], "/login")

    def test_log_dir_is_created(self):
        import config
        new_dir = os.path.join(self.tmpdir, "nested", "logs")
        new_file = os.path.join(new_dir, "hp.log")
        with patch.object(config, "LOG_DIR", new_dir), \
             patch.object(config, "LOG_FILE", new_file):
            # Re-import to trigger os.makedirs – or call it directly
            os.makedirs(new_dir, exist_ok=True)
            import logger as hplog
            hplog.log_attempt("SSH", "1.1.1.1", 22)
        self.assertTrue(os.path.isdir(new_dir))


# ---------------------------------------------------------------------------
# FTP service
# ---------------------------------------------------------------------------

class TestFTPService(unittest.TestCase):
    """Integration test: spin up the FTP honeypot on a random port."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.tmpdir, "ftp.log")
        self.port = _free_port()

    def _start_ftp(self):
        import config
        import logger as hplog
        from services import ftp_server

        with patch.object(config, "FTP_PORT", self.port), \
             patch.object(config, "LOG_FILE", self.log_file):
            ftp_server.start()

    def test_ftp_logs_credentials(self):
        import config
        import logger as hplog
        from services import ftp_server

        port = self.port

        def _run():
            with patch.object(config, "FTP_PORT", port), \
                 patch.object(config, "LOG_FILE", self.log_file):
                ftp_server.start()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        time.sleep(0.3)

        # Connect as a fake attacker
        with socket.create_connection(("127.0.0.1", port), timeout=5) as s:
            banner = s.recv(256).decode()
            self.assertIn("220", banner)

            s.sendall(b"USER testuser\r\n")
            resp = s.recv(256).decode()
            self.assertIn("331", resp)

            s.sendall(b"PASS testpass\r\n")
            resp = s.recv(256).decode()
            self.assertIn("530", resp)

            s.sendall(b"QUIT\r\n")

        time.sleep(0.2)
        with open(self.log_file, encoding="utf-8") as fh:
            records = [json.loads(l) for l in fh if l.strip()]

        cred_records = [r for r in records if r.get("username")]
        self.assertTrue(len(cred_records) >= 1)
        self.assertEqual(cred_records[0]["username"], "testuser")
        self.assertEqual(cred_records[0]["password"], "testpass")
        self.assertEqual(cred_records[0]["service"], "FTP")


# ---------------------------------------------------------------------------
# HTTP service
# ---------------------------------------------------------------------------

class TestHTTPService(unittest.TestCase):
    """Integration test: spin up the HTTP honeypot on a random port."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.tmpdir, "http.log")
        self.port = _free_port()

    def test_http_serves_login_page(self):
        import urllib.request
        import config
        from services import http_server

        port = self.port

        def _run():
            with patch.object(config, "HTTP_PORT", port), \
                 patch.object(config, "LOG_FILE", self.log_file):
                http_server.start()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        time.sleep(0.3)

        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5)
        body = resp.read().decode()
        self.assertIn("<form", body)
        self.assertIn("password", body.lower())

    def test_http_logs_post_credentials(self):
        import urllib.request
        import urllib.parse
        import config
        from services import http_server

        port = self.port

        def _run():
            with patch.object(config, "HTTP_PORT", port), \
                 patch.object(config, "LOG_FILE", self.log_file):
                http_server.start()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        time.sleep(0.3)

        data = urllib.parse.urlencode({"username": "admin", "password": "hunter2"}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/login",
            data=data,
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)

        time.sleep(0.2)
        with open(self.log_file, encoding="utf-8") as fh:
            records = [json.loads(l) for l in fh if l.strip()]

        cred_records = [r for r in records if r.get("username")]
        self.assertTrue(len(cred_records) >= 1)
        self.assertEqual(cred_records[0]["username"], "admin")
        self.assertEqual(cred_records[0]["password"], "hunter2")
        self.assertEqual(cred_records[0]["service"], "HTTP")


# ---------------------------------------------------------------------------
# Telnet service
# ---------------------------------------------------------------------------

class TestTelnetService(unittest.TestCase):
    """Integration test: spin up the Telnet honeypot on a random port."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.tmpdir, "telnet.log")
        self.port = _free_port()

    def test_telnet_logs_credentials(self):
        import config
        from services import telnet_server

        port = self.port

        def _run():
            with patch.object(config, "TELNET_PORT", port), \
                 patch.object(config, "LOG_FILE", self.log_file):
                telnet_server.start()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        time.sleep(0.3)

        with socket.create_connection(("127.0.0.1", port), timeout=5) as s:
            banner = s.recv(256)
            self.assertIn(b"login", banner.lower())

            s.sendall(b"root\r\n")
            time.sleep(0.1)
            prompt = s.recv(256)
            self.assertIn(b"Password", prompt)

            s.sendall(b"toor\r\n")
            time.sleep(0.1)

        time.sleep(0.2)
        with open(self.log_file, encoding="utf-8") as fh:
            records = [json.loads(l) for l in fh if l.strip()]

        cred_records = [r for r in records if r.get("username")]
        self.assertTrue(len(cred_records) >= 1)
        self.assertEqual(cred_records[0]["username"], "root")
        self.assertEqual(cred_records[0]["password"], "toor")
        self.assertEqual(cred_records[0]["service"], "TELNET")


if __name__ == "__main__":
    unittest.main()
