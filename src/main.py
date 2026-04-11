import socket
import paramiko
import threading
import time
import os
import json
from urllib.parse import parse_qs, urlparse

from logger import AttackLogger
from ssh_module import LureServer
from owasp_honeypot import OWASPHoneypot, OWASPDetector

ip_test = "126.253.0.1"

def handle_conn(client, ip_source, log, hostKey):
    transport = paramiko.Transport(client)
    transport.add_server_key(hostKey)
    server = LureServer(ip_source, log)
    try:
        transport.start_server(server=server)
        chan = transport.accept(30)
        if chan is not None:
            server.event.wait(10)
            server.handle_shell(chan)
    except Exception as e:
        pass


def http_lure(log):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    honeypot = OWASPHoneypot(log)
    detector = OWASPDetector()
    http_login_attempts = {} # Dictionnaire pour suivre le timing des tentatives de login

    try:
        server_socket.bind(('0.0.0.0', 8080))
        server_socket.listen(5)
        print("[*] HTTP Lure est en ligne sur le port 8080")
    except Exception as e:
        print(f"[-] Erreur HTTP Lure : {e}")
        return

    while True:
        client, addr = server_socket.accept()
        try:
            data = client.recv(4096).decode(errors='ignore')

            if data:
                lines = data.splitlines()
                request_line = lines[0] if lines else ""

                # Extraction du User-Agent et des headers
                user_agent = "Unknown"
                headers = {}
                for line in lines:
                    if line.startswith("User-Agent:"):
                        user_agent = line.replace("User-Agent:", "").strip()
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        headers[key] = value

                # Détecte le scanner
                scanner = detector.detect_scanner(user_agent)

                # Parse la requête
                method = request_line.split()[0] if request_line else "UNKNOWN"
                path = request_line.split()[1] if len(request_line.split()) > 1 else "/"

                # ========== PAGE 1: LOGIN SIMPLE ==========
                if path.startswith("/login") or path == "/":
                    if method == "POST":
                        # Détection de Brute Force
                        ip = addr[0]
                        current_time = time.time()
                        if ip in http_login_attempts and current_time - http_login_attempts.get(ip, 0) < 2.0: # Moins de 2s
                            log.log_attempt(ip, "HTTP_BRUTE_FORCE", "FAST_ATTEMPT", None, "ATTACK", "Brute force attempt detected", user_agent)
                        http_login_attempts[ip] = current_time

                        # Récupère le body
                        body = data.split("\r\n\r\n")[-1] if "\r\n\r\n" in data else ""

                        # Vérifie si on dépasse 3 tentatives
                        if honeypot.check_login_attempts(addr[0]):
                            # REDIRECTION vers honeypot OWASP avancé
                            response_text = honeypot.generate_fake_app()
                            log.log_attempt(addr[0], "HTTP_LOGIN", "REDIRECTED_TO_OWASP", "3_FAILED_ATTEMPTS", "TRAP", f"Attacker redirected to OWASP honeypot", user_agent)
                        else:
                            # Première tentative - on refuse simplement
                            response_text = '<html><body><h2>Login Failed</h2><p>Invalid username or password. <a href="/">Try again</a></p></body></html>'
                            log.log_attempt(addr[0], "HTTP_LOGIN", "LOGIN_FAILED", body, "RECON", None, user_agent)
                    else:
                        # Page de login simple
                        response_text = """
                        <html><body style="text-align:center; padding-top:100px; font-family:sans-serif;">
                            <div style="background:#eee; width:300px; margin:auto; padding:20px; border:1px solid #ccc;">
                                <h2>Admin Login</h2>
                                <form method="POST" action="/login">
                                    <input name="user" placeholder="User"><br><br>
                                    <input name="pass" type="password" placeholder="Pass"><br><br>
                                    <input type="submit" value="Login">
                                </form>
                            </div>
                        </body></html>
                        """
                        log.log_attempt(addr[0], "HTTP", "WebScanner", request_line, "RECON", None, user_agent)

                # ========== PAGE 2: HONEYPOT OWASP AVANCÉ ==========
                elif path.startswith("/profile"):
                    # Endpoint vulnérable: SQLi
                    params = dict(parse_qs(path.split("?")[1]) if "?" in path else {})
                    user_id = params.get("user_id", [""])[0] if "user_id" in params else ""
                    attacks = honeypot.process_vulnerable_endpoint("/profile", user_id, addr[0], user_agent)
                    attack_type = list(attacks.keys())[0] if attacks else "SQLI"

                    # Log avec les nouveaux champs
                    scanner = detector.detect_scanner(user_agent)
                    log.log_attempt(addr[0], "HTTP_ATTACK", None, None, "ATTACK", user_id, user_agent,
                                  attack_type=attack_type, endpoint="/profile", payload=user_id,
                                  http_method="GET", scanner_name=scanner,
                                  headers=json.dumps(headers), response_code=200)

                    # Réponse réaliste
                    response_text = f"""<html><body>
                    <h2>User Profile</h2>
                    <table border="1">
                    <tr><td>ID</td><td>{user_id}</td></tr>
                    <tr><td>Name</td><td>John Doe</td></tr>
                    <tr><td>Email</td><td>john@example.com</td></tr>
                    <tr><td>Role</td><td>Admin</td></tr>
                    </table>
                    </body></html>"""

                elif path.startswith("/search"):
                    # Endpoint vulnérable: XSS + SQLi
                    body = data.split("\r\n\r\n")[-1] if "\r\n\r\n" in data else ""
                    attacks = honeypot.process_vulnerable_endpoint("/search", body, addr[0], user_agent)
                    attack_type = list(attacks.keys())[0] if attacks else "XSS"

                    # Log avec les nouveaux champs
                    scanner = detector.detect_scanner(user_agent)
                    log.log_attempt(addr[0], "HTTP_ATTACK", None, None, "ATTACK", body, user_agent,
                                  attack_type=attack_type, endpoint="/search", payload=body,
                                  http_method="POST", scanner_name=scanner,
                                  headers=json.dumps(headers), response_code=200)

                    # Réponse réaliste
                    response_text = f"""<html><body>
                    <h2>Search Results</h2>
                    <p>Found 42 users matching your query</p>
                    <ul>
                    <li>User 1 - admin@example.com</li>
                    <li>User 2 - test@example.com</li>
                    </ul>
                    </body></html>"""

                elif path.startswith("/file"):
                    # Endpoint vulnérable: LFI + RFI
                    params = dict(parse_qs(path.split("?")[1]) if "?" in path else {})
                    file_path = params.get("path", [""])[0] if "path" in params else "/var/www/html"
                    attacks = honeypot.process_vulnerable_endpoint("/file", file_path, addr[0], user_agent)
                    attack_type = list(attacks.keys())[0] if attacks else "LFI"

                    # Log avec les nouveaux champs
                    scanner = detector.detect_scanner(user_agent)
                    log.log_attempt(addr[0], "HTTP_ATTACK", None, None, "ATTACK", file_path, user_agent,
                                  attack_type=attack_type, endpoint="/file", payload=file_path,
                                  http_method="GET", scanner_name=scanner,
                                  headers=json.dumps(headers), response_code=200)

                    # Réponse réaliste
                    response_text = f"""<html><body>
                    <h2>File Manager</h2>
                    <p>Current path: {file_path}</p>
                    <ul>
                    <li>index.php (1.2 KB)</li>
                    <li>config.php (2.8 KB)</li>
                    <li>database.sql (45.6 KB)</li>
                    <li>admin/</li>
                    </ul>
                    </body></html>"""

                elif path.startswith("/api"):
                    # Endpoint vulnérable: SSRF + XXE
                    params = dict(parse_qs(path.split("?")[1]) if "?" in path else {})
                    target_url = params.get("url", [""])[0] if "url" in params else ""
                    attacks = honeypot.process_vulnerable_endpoint("/api", target_url, addr[0], user_agent)
                    attack_type = list(attacks.keys())[0] if attacks else "SSRF"

                    # Log avec les nouveaux champs
                    scanner = detector.detect_scanner(user_agent)
                    log.log_attempt(addr[0], "HTTP_ATTACK", None, None, "ATTACK", target_url, user_agent,
                                  attack_type=attack_type, endpoint="/api", payload=target_url,
                                  http_method="GET", scanner_name=scanner,
                                  headers=json.dumps(headers), response_code=200)

                    # Réponse réaliste
                    response_text = f"""<html><body>
                    <h2>API Endpoint</h2>
                    <pre>
                    {{
                        "status": "success",
                        "endpoint": "{target_url}",
                        "data": [
                            {{"id": 1, "name": "Resource 1"}},
                            {{"id": 2, "name": "Resource 2"}}
                        ]
                    }}
                    </pre>
                    </body></html>"""

                else:
                    response_text = honeypot.generate_fake_app()

                # Envoi de la réponse CORRECTE
                response_bytes = response_text.encode('utf-8')
                content_length = len(response_bytes)
                header = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n"
                client.sendall(header.encode('utf-8') + response_bytes)

        except Exception as e:
            print(f"[-] Erreur HTTP : {e}")
        finally:
            client.close()


def ssh_listener(log, hostKey):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(100)

    print(f"[*] AttackMyLure est en ligne sur le port 2222")

    while True:
        client, addr = server_socket.accept()

        t = threading.Thread(target=handle_conn, args=(client, addr[0], log, hostKey))
        t.start()

def start_server():
    log = AttackLogger()

    # Clé fixe
    key_file = "private_key.key"

    if os.path.exists(key_file):
        print("[*] Loading SSH KEY")
        hostKey = paramiko.RSAKey.from_private_key_file(key_file)
    else:
        print("[*] Creating SSH KEY")
        hostKey = paramiko.RSAKey.generate(2048)
        hostKey.write_private_key_file(key_file)

    # On lance le thread SSH
    threading.Thread(target=ssh_listener, args=(log, hostKey), daemon=True).start()

    # On lance le thread HTTP
    threading.Thread(target=http_lure, args=(log,), daemon=True).start()

    print("[*] Système Multi-Leurre activé. Bonne chasse !")
    print("[*] OWASP Honeypot: Pages avancées activées après 3 tentatives échouées")

    # Boucle infinie pour empêcher le script de s'arrêter
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Fermeture du Honeypot...")

if __name__ == '__main__':
    start_server()
