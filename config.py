"""
AttackMyLure – Honeypot configuration.
Edit this file to customise ports, banners and logging behaviour.
"""

import os

# ---------------------------------------------------------------------------
# Network settings
# ---------------------------------------------------------------------------

# Each entry is (host, port).  Use "0.0.0.0" to listen on all interfaces.
SSH_HOST = "0.0.0.0"
SSH_PORT = 2222          # Use 22 if running as root

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8080         # Use 80 if running as root

FTP_HOST = "0.0.0.0"
FTP_PORT = 2121          # Use 21 if running as root

TELNET_HOST = "0.0.0.0"
TELNET_PORT = 2323       # Use 23 if running as root

# ---------------------------------------------------------------------------
# Service banners / identification strings
# ---------------------------------------------------------------------------

SSH_BANNER = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6"
FTP_BANNER = "220 FTP server ready."
TELNET_BANNER = b"\r\nUbuntu 22.04 LTS\r\n\r\nlogin: "
HTTP_TITLE = "Router Management Console"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "honeypot.log")

# ---------------------------------------------------------------------------
# Fake RSA host key (generated on first run and stored here)
# ---------------------------------------------------------------------------

HOST_KEY_FILE = os.path.join(os.path.dirname(__file__), "host.key")

# ---------------------------------------------------------------------------
# Maximum connection backlog per service
# ---------------------------------------------------------------------------

BACKLOG = 5
