import threading

import paramiko

class LureServer(paramiko.ServerInterface):
    def __init__(self, client_ip , logger):
        self.client_ip = client_ip
        self.logger = logger
        self.event = threading.Event()

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
        channel.send("\r\nLinux debian 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4\r\n")
        channel.send("Last login: Fri Oct 27 10:12:44 2023 from 192.168.1.45\r\n")

        prompt = "root@debian:~# "
        channel.send(prompt)

        command = ""
        while True:
            try:
                # On reçoit les touches une par une
                char = channel.recv(1).decode(errors='ignore')

                if not char:
                    break

                # Si Entrée
                if char == "\r" or char == "\n":
                    channel.send("\r\n")
                    if command.strip():
                        print(f"[!!!] COMMANDE de {self.client_ip}: {command}")
                        # On log la commande comme si c'était un "password" pour réutiliser ton logger
                        print(f"[!!!] COMMANDE : {command}")
                        self.logger.log_attempt(self.client_ip, "COMMAND", "root", None, "SHELL", command, "UNKNOWN")

                        # Réponse systématique "commande introuvable"
                        channel.send(f"-bash: {command.split()[0]}: command not found\r\n")

                    command = ""
                    channel.send(prompt)

                # Si Retour arrière (BackSpace)
                elif char == "\x7f" or char == "\x08":
                    if len(command) > 0:
                        command = command[:-1]
                        channel.send("\b \b")  # Efface visuellement le caractère

                # On ne traite pas les flèches directionnelles (trop complexe pour un début)
                elif char == "\x1b":
                    continue

                # Sinon on accumule les caractères
                else:
                    command += char
                    channel.send(char)  # Echo pour que l'attaquant voit ce qu'il tape

            except:
                break

        channel.close()