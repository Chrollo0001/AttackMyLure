import mysql.connector
from datetime import datetime
import requests



class AttackLogger:
    def __init__(self):
        # Configuration de la connexion XAMPP
        self.config = {
            'user': 'root',
            'password': '',
            'host': '127.0.0.1',
            'database': 'attack_my_lure'
        }

    def get_ip_info(self, ip):
        if ip == "127.0.0.1" or ip == "localhost":
            return "France", "Localhost", "Internal Network"

        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
            if response.get('status') == 'success':
                return (
                    response.get('country', 'Unknown'),
                    response.get('city', 'Unknown'),
                    response.get('isp', 'Unknown')
                )
        except Exception as e:
            print(f"[-] Erreur GeoIP : {e}")

        return "Unknown", "Unknown", "Unknown"

    def log_attempt(self, ip, protocol, username, password , client_version="UNKNOWN"):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        country, city, isp = self.get_ip_info(ip)
        try:
            # Connexion à MySQL
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            sql = """INSERT INTO attacks
                    (timestamp, protocol, ip_address, country, city, isp, username, password, client_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            values = (now, protocol, ip, country, city, isp, username, password, client_version)

            cursor.execute(sql, values)
            conn.commit()

            print(f"[*] [MySQL] Succès : {username}:{password} enregistré.")

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"[-] Erreur MySQL : {err}")