"""
AttackMyLure – Fake Telnet honeypot service.

Presents a Unix-style login prompt.  Every username / password pair is
logged; access is always denied with "Login incorrect".
"""

import socket
import threading

import config
import logger as hplog

_INCORRECT = b"\r\nLogin incorrect\r\n\r\n"
_PASSWORD_PROMPT = b"Password: "


# ---------------------------------------------------------------------------
# Per-connection handler
# ---------------------------------------------------------------------------

def _recv_line(sock: socket.socket) -> str:
    """Read until CRLF or LF, returning decoded text (strips line ending)."""
    buf = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            break
        if ch in (b"\r", b"\n"):
            # consume the paired character if present
            sock.setblocking(False)
            try:
                nxt = sock.recv(1)
                if nxt not in (b"\r", b"\n"):
                    buf += nxt
            except (BlockingIOError, OSError):
                pass
            finally:
                sock.setblocking(True)
            break
        # Strip Telnet IAC negotiation bytes (0xFF …)
        if ch == b"\xff":
            sock.recv(2)  # option + sub-option
            continue
        buf += ch
    return buf.decode(errors="replace")


def _handle_connection(sock: socket.socket, client_address: tuple[str, int]) -> None:
    src_ip, src_port = client_address
    hplog.log_attempt("TELNET", src_ip, src_port)

    try:
        sock.sendall(config.TELNET_BANNER)

        username = _recv_line(sock)
        sock.sendall(_PASSWORD_PROMPT)
        password = _recv_line(sock)

        hplog.log_attempt(
            "TELNET",
            src_ip,
            src_port,
            username=username,
            password=password,
        )

        sock.sendall(_INCORRECT)

    except OSError:
        pass
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the Telnet honeypot service (blocking – run in a thread)."""

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((config.TELNET_HOST, config.TELNET_PORT))  # lgtm[py/bind-socket-all-network-interfaces]
    srv.listen(config.BACKLOG)
    hplog.logger.info(
        "TELNET honeypot listening on %s:%d",
        config.TELNET_HOST,
        config.TELNET_PORT,
    )

    while True:
        try:
            client_sock, client_addr = srv.accept()
            t = threading.Thread(
                target=_handle_connection,
                args=(client_sock, client_addr),
                daemon=True,
            )
            t.start()
        except OSError:
            break
