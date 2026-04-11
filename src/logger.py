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

    def get_advanced_ip_info(self, ip):
        if ip in ["127.0.0.1", "localhost", ]:  # On ignore tes IPs de test
            return "France", "Localhost", "Internal", "AS000", 0,0

        try:
            # Utilisation de ip-api.com (version pro ou gratuite avec champs spécifiques)
            # On demande : pays, ville, isp, asn, et proxy (mobile/proxy)
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,as,mobile,proxy,hosting"
            response = requests.get(url, timeout=5).json()

            if response.get('status') == 'success':
                is_vpn = 1 if (response.get('proxy') or response.get('hosting')) else 0
                threat_score = 50 if is_vpn else 10  # Score arbitraire pour commencer

                return (
                    response.get('country', 'Unknown'),
                    response.get('city', 'Unknown'),
                    response.get('isp', 'Unknown'),
                    response.get('as', 'Unknown'),  # ASN
                    is_vpn,
                    threat_score
                )
        except Exception as e:
            print(f"[-] Erreur GeoIP Avancée : {e}")

        return "Unknown", "Unknown", "Unknown", "Unknown", 0, 0

    def log_attempt(self, ip, protocol, username, password, status, command=None, client_version="UNKNOWN",
                    attack_type=None, endpoint=None, payload=None, http_method=None, scanner_name=None, headers=None, response_code=200):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # On récupère les nouvelles infos
        country, city, isp, asn, is_vpn, threat_score = self.get_advanced_ip_info(ip)

        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            sql = """INSERT INTO attacks
                     (ip_address, protocol, username, password, status, command, client_version,
                      timestamp, country, city, isp, asn, is_vpn, threat_score,
                      attack_type, endpoint, payload, http_method, scanner_name, headers, response_code)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            values = (ip, protocol, username, password, status, command, client_version,
                      now, country, city, isp, asn, is_vpn, threat_score,
                      attack_type, endpoint, payload, http_method, scanner_name, headers, response_code)

            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"[-] Erreur MySQL : {err}")