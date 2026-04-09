"""
AttackMyLure – Fake SSH honeypot service.

Uses *paramiko* to present a realistic SSH server.  Every authentication
attempt (including username and password) is logged; no session is ever
granted real access.
"""

import socket
import threading

import paramiko

import config
import logger as hplog


# ---------------------------------------------------------------------------
# SSH server interface (authentication always fails after logging)
# ---------------------------------------------------------------------------

class _HoneypotServerInterface(paramiko.ServerInterface):
    """Paramiko server interface that logs then rejects every auth attempt."""

    def __init__(self, client_address: tuple[str, int]) -> None:
        self._ip, self._port = client_address

    # --- authentication ----------------------------------------------------

    def check_auth_password(self, username: str, password: str) -> int:
        hplog.log_attempt(
            "SSH",
            self._ip,
            self._port,
            username=username,
            password=password,
        )
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        hplog.log_attempt(
            "SSH",
            self._ip,
            self._port,
            username=username,
            extra={"auth_type": "publickey", "key_type": key.get_name()},
        )
        return paramiko.AUTH_FAILED

    def check_auth_none(self, username: str) -> int:
        return paramiko.AUTH_FAILED

    # --- channel / session requests ----------------------------------------

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username: str) -> str:
        return "password,publickey"


# ---------------------------------------------------------------------------
# Per-connection handler
# ---------------------------------------------------------------------------

def _handle_connection(
    sock: socket.socket,
    client_address: tuple[str, int],
    host_key: paramiko.RSAKey,
) -> None:
    transport = None
    try:
        transport = paramiko.Transport(sock)
        transport.local_version = config.SSH_BANNER
        transport.add_server_key(host_key)

        server = _HoneypotServerInterface(client_address)
        transport.start_server(server=server)

        # Wait briefly – enough for auth negotiation to complete
        chan = transport.accept(20)
        if chan is not None:
            chan.close()
    except (paramiko.SSHException, OSError):
        pass
    finally:
        if transport and transport.is_active():
            transport.close()
        sock.close()


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def start() -> None:
    """Start the SSH honeypot service (blocking – run in a thread)."""

    # Load or generate the RSA host key
    try:
        host_key = paramiko.RSAKey(filename=config.HOST_KEY_FILE)
        hplog.logger.info("SSH: loaded host key from %s", config.HOST_KEY_FILE)
    except (FileNotFoundError, paramiko.SSHException):
        host_key = paramiko.RSAKey.generate(2048)
        host_key.write_private_key_file(config.HOST_KEY_FILE)
        hplog.logger.info("SSH: generated new host key → %s", config.HOST_KEY_FILE)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((config.SSH_HOST, config.SSH_PORT))  # lgtm[py/bind-socket-all-network-interfaces]
    srv.listen(config.BACKLOG)
    hplog.logger.info("SSH honeypot listening on %s:%d", config.SSH_HOST, config.SSH_PORT)

    while True:
        try:
            client_sock, client_addr = srv.accept()
            t = threading.Thread(
                target=_handle_connection,
                args=(client_sock, client_addr, host_key),
                daemon=True,
            )
            t.start()
        except OSError:
            break
