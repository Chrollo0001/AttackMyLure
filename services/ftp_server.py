"""
AttackMyLure – Fake FTP honeypot service.

Implements just enough of RFC 959 to attract brute-force tools:
  • Sends a 220 banner
  • Accepts USER and PASS commands (and logs credentials)
  • Always responds with 530 Login incorrect
  • Responds 500 to everything else
"""

import socket
import threading

import config
import logger as hplog


# ---------------------------------------------------------------------------
# Per-connection handler
# ---------------------------------------------------------------------------

def _handle_connection(sock: socket.socket, client_address: tuple[str, int]) -> None:
    src_ip, src_port = client_address
    hplog.log_attempt("FTP", src_ip, src_port)

    try:
        sock.sendall((config.FTP_BANNER + "\r\n").encode())
        username = ""

        while True:
            data = sock.recv(1024)
            if not data:
                break
            line = data.decode(errors="replace").strip()
            cmd = line[:4].upper()

            if cmd == "USER":
                username = line[5:].strip()
                sock.sendall(b"331 Password required for " + username.encode() + b"\r\n")

            elif cmd == "PASS":
                password = line[5:].strip()
                hplog.log_attempt(
                    "FTP",
                    src_ip,
                    src_port,
                    username=username,
                    password=password,
                )
                sock.sendall(b"530 Login incorrect.\r\n")

            elif cmd == "QUIT":
                sock.sendall(b"221 Goodbye.\r\n")
                break

            else:
                sock.sendall(b"500 Unknown command.\r\n")

    except OSError:
        pass
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the FTP honeypot service (blocking – run in a thread)."""

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((config.FTP_HOST, config.FTP_PORT))  # lgtm[py/bind-socket-all-network-interfaces]
    srv.listen(config.BACKLOG)
    hplog.logger.info(
        "FTP honeypot listening on %s:%d", config.FTP_HOST, config.FTP_PORT
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
