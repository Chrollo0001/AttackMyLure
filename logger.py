"""
AttackMyLure – centralised logging module.

All honeypot services call ``log_attempt`` to record connection events.
Events are written as JSON lines to the log file configured in ``config.py``
and are also emitted to the standard Python logging facility so they appear
on the console.
"""

import json
import logging
import os
from datetime import datetime, timezone

import config

# ---------------------------------------------------------------------------
# Ensure the log directory exists
# ---------------------------------------------------------------------------
os.makedirs(config.LOG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Python logging setup
# ---------------------------------------------------------------------------
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

_file_handler = logging.FileHandler(config.LOG_FILE)
_file_handler.setFormatter(_fmt)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_fmt)

logger = logging.getLogger("honeypot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(_file_handler)
    logger.addHandler(_console_handler)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_attempt(
    service: str,
    src_ip: str,
    src_port: int,
    *,
    username: str = "",
    password: str = "",
    extra: dict | None = None,
) -> None:
    """Record one connection / credential-harvest attempt.

    Parameters
    ----------
    service:
        Name of the honeypot service that received the attempt
        (e.g. ``"SSH"``, ``"HTTP"``, ``"FTP"``, ``"TELNET"``).
    src_ip:
        Remote IP address.
    src_port:
        Remote TCP port.
    username:
        Username supplied by the attacker (if any).
    password:
        Password supplied by the attacker (if any).
    extra:
        Any additional key/value data to include in the log record.
    """
    record: dict = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "service": service,
        "src_ip": src_ip,
        "src_port": src_port,
    }
    if username:
        record["username"] = username
    if password:
        record["password"] = password
    if extra:
        record.update(extra)

    # Write JSON line to log file
    try:
        with open(config.LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError as exc:
        logger.error("Failed to write log entry: %s", exc)

    # Human-readable console / file log via Python logging
    msg = "[%s] %s:%d" % (service, src_ip, src_port)
    if username:
        msg += "  user=%r" % username
    if password:
        msg += "  pass=%r" % password  # lgtm[py/clear-text-logging-sensitive-data]
    logger.info(msg)
