import re
import threading
import requests
import os

import paramiko

class LureServer(paramiko.ServerInterface):
    def __init__(self, client_ip , logger):
        self.client_ip = client_ip
        self.logger = logger
        self.event = threading.Event()

    def capture_payload(self, command):
        # Chemin absolu vers le dossier captured_payloads
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(script_dir, "captured_payloads")

        # Regex Find URL
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', command)

        for url in urls:
            try:
                print(f"[!] CIBLE DÉTECTÉE : {url}. Tentative de capture...")

                # On crée le dossier s'il n'existe pas
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    print(f"[*] Dossier créé : {target_dir}")

                # Téléchargement sécurisé
                print(f"[*] Téléchargement depuis : {url}")
                response = requests.get(url, timeout=5, stream=True)
                print(f"[*] Status code: {response.status_code}")

                if response.status_code == 200:
                    # On nettoie le nom du fichier
                    filename = url.split("/")[-1] or "index.html"
                    filepath = os.path.join(target_dir, f"{self.client_ip}_{filename}")

                    with open(filepath, "wb") as f:
                        f.write(response.content)

                    file_size = os.path.getsize(filepath)
                    print(f"[+++] SUCCÈS : Script volé -> {filepath} ({file_size} bytes)")
                else:
                    print(f"[?] Code HTTP {response.status_code} pour {url}")

            except requests.exceptions.Timeout:
                print(f"[-] Timeout lors du téléchargement de {url}")
            except requests.exceptions.ConnectionError as e:
                print(f"[-] Erreur de connexion pour {url} : {e}")
            except Exception as e:
                print(f"[-] Erreur lors de la capture de {url} : {e}")

    def check_auth_password(self, username, password):
        print(f"[*] Tentative de connexion SSH de {self.client_ip} avec le nom d'utilisateur '{username}' et le mot de passe '{password}'")
        client_ver = self.logger.client_version if hasattr(self.logger, 'client_version') else "UNKNOWN"
        self.logger.log_attempt(self.client_ip , "SSH", username , password, client_ver, "SUCCESS")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def handle_shell(self, channel):
        fake_fs = {
            '/etc/passwd': 'root:x:0:0:root:/root:/bin/bash\nbin:x:1:1:bin:/bin:/sbin/nologin\ndaemon:x:2:2:daemon:/sbin:/sbin/nologin',
            '/root/.bash_history': 'ls -la\ncat /etc/passwd\nuname -a\n',
            '/var/log/auth.log': 'Oct 27 10:12:44 debian sshd[1234]: Accepted password for root from 192.168.1.45 port 54321 ssh2'
        }
        current_dir = '/root'

        channel.send("\r\nLinux debian 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4\r\n")
        channel.send("Last login: Fri Oct 27 10:12:44 2023 from 192.168.1.45\r\n")

        prompt = "root@debian:~# "
        channel.send(prompt)

        command = ""
        while True:
            try:
                char = channel.recv(1).decode(errors='ignore')
                if not char:
                    break

                if char == "\r" or char == "\n":
                    channel.send("\r\n")
                    clean_cmd = command.strip()

                    if clean_cmd:
                        print(f"[!!!] COMMANDE de {self.client_ip}: {clean_cmd}")
                        self.logger.log_attempt(self.client_ip, "COMMAND", "root", None, "SHELL", clean_cmd, "UNKNOWN")

                        # --- SIMULATION D'ENVIRONNEMENT RICHE ---
                        parts = clean_cmd.split()
                        cmd_name = parts[0]
                        response = ""

                        if cmd_name == 'whoami':
                            response = "root\r\n"
                        elif cmd_name == 'uname' and '-a' in parts:
                            response = "Linux debian 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4 x86_64 GNU/Linux\r\n"
                        elif cmd_name == 'cat':
                            if len(parts) > 1 and parts[1] in fake_fs:
                                response = fake_fs[parts[1]] + "\r\n"
                                self.logger.log_attempt(self.client_ip, "FILE_READ", "root", None, "SHELL", f"Read sensitive file: {parts[1]}", "UNKNOWN")
                            else:
                                response = f"cat: {parts[1]}: No such file or directory\r\n"
                        elif cmd_name == 'ls':
                            response = "total 0\r\n-rw-r--r-- 1 root root 0 Oct 27 10:10 .bash_history\r\n"
                        elif cmd_name == 'ps' and 'aux' in parts:
                            response = "USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\r\n"
                            response += "root           1  0.0  0.1  10668  3440 ?        Ss   Oct26   0:02 /sbin/init\r\n"
                            response += "root         234  0.0  0.2  56344  5380 ?        Ssl  Oct26   0:15 /usr/sbin/sshd -D\r\n"
                        elif "curl" in cmd_name or "wget" in cmd_name:
                            self.capture_payload(clean_cmd)
                            response = "Connecting to host... done.\r\n"
                        else:
                            response = f"-bash: {cmd_name}: command not found\r\n"

                        channel.send(response)

                    command = ""
                    channel.send(prompt)

                elif char == "\x7f" or char == "\x08":
                    if len(command) > 0:
                        command = command[:-1]
                        channel.send("\b \b")

                elif char == "\x1b":
                    continue

                else:
                    command += char
                    channel.send(char)

            except Exception as e:
                print(f"Erreur shell : {e}")
                break

        channel.close()