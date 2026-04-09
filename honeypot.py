#!/usr/bin/env python3
"""
AttackMyLure – Honeypot entry-point.

Starts all configured honeypot services (SSH, HTTP, FTP, Telnet) in daemon
threads and then waits for a keyboard interrupt.

Usage
-----
    python honeypot.py

All connection attempts are logged to ``logs/honeypot.log`` (JSON lines) and
printed to the console.
"""

import signal
import sys
import threading

import config  # noqa: F401 – imported to ensure LOG_DIR is created via logger
import logger as hplog
from services import ftp_server, http_server, ssh_server, telnet_server


def _start_daemon(target, name: str) -> threading.Thread:
    """Start *target* in a daemon thread named *name*."""
    t = threading.Thread(target=target, name=name, daemon=True)
    t.start()
    return t


def main() -> None:
    hplog.logger.info("AttackMyLure honeypot starting …")

    services = [
        (ssh_server.start, "SSH-honeypot"),
        (http_server.start, "HTTP-honeypot"),
        (ftp_server.start, "FTP-honeypot"),
        (telnet_server.start, "TELNET-honeypot"),
    ]

    threads = [_start_daemon(fn, name) for fn, name in services]

    hplog.logger.info(
        "All services up.  Listening on ports SSH=%d  HTTP=%d  FTP=%d  TELNET=%d",
        config.SSH_PORT,
        config.HTTP_PORT,
        config.FTP_PORT,
        config.TELNET_PORT,
    )
    hplog.logger.info("Press Ctrl+C to stop.")

    # Keep the main thread alive; handle SIGTERM gracefully
    def _shutdown(signum, frame):
        hplog.logger.info("Received signal %d – shutting down.", signum)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        hplog.logger.info("KeyboardInterrupt – shutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()
