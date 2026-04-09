import paramiko

class LureServer(paramiko.ServerInterface):
    def __init__(self, client_ip , logger):
        self.client_ip = client_ip
        self.logger = logger

    def check_auth_password(self, username, password):
        print(f"[*] Tentative de connexion SSH de {self.client_ip} avec le nom d'utilisateur '{username}' et le mot de passe '{password}'")
        client_ver = self.logger.client_version if hasattr(self.logger, 'client_version') else "UNKNOWN"
        self.logger.log_attempt(self.client_ip , "SSH", username , password, client_ver)
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED