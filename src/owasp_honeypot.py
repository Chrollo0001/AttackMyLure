"""
OWASP Honeypot - Fake App pour capturer les attaques web avancées
Détecte: SQLi, XSS, SSRF, CSRF, LFI, RFI, RCE, File Upload, etc.
"""
import re
import json
from urllib.parse import quote, unquote

class OWASPDetector:
    """Détecte les patterns d'attaques OWASP"""

    # Patterns dangereux
    PATTERNS = {
        'SQLI': [
            r"(\bOR\b|\bAND\b)\s*['\"]?\s*=\s*['\"]",  # OR 1=1, AND 1=1
            r"(\bunion\b.*\bselect\b|\bselect\b.*\bunion\b)",  # UNION SELECT
            r"(\bdrop\b|\btruncate\b|\bdelete\b)\s+(\btable\b|\bdatabase\b)",  # DROP/DELETE
            r"(';|\";\s*--|#)",  # Comment injection
            r"(\\\\/|\\x)",  # Hex encoding
        ],
        'XSS': [
            r"(<script[^>]*>|javascript:|on\w+\s*=|<iframe|<img)",  # Script tags
            r"(alert\(|console\.log|eval\()",  # JS execution
            r"(<svg|<body|onerror=|onload=)",  # Event handlers
        ],
        'SSRF': [
            r"(file://|http://127\.0\.0\.1|http://localhost|http://169\.254)",  # Internal IPs
            r"(http://10\.|http://172\.|http://192\.168\.)",  # Private IPs
        ],
        'LFI': [
            r"(\.\./|\.\.\\|%2e%2e|%252e)",  # Directory traversal
            r"(etc/passwd|etc\\windows\\win\.ini|windows/system32)",  # Known files
        ],
        'RFI': [
            r"(http://|https://|ftp://)[^\s]*\.(php|txt|sh|exe|aspx)",  # Remote file inclusion
        ],
        'RCE': [
            r"(exec\(|system\(|passthru\(|shell_exec\()",  # Code execution
            r"(rm\s+-|nc\s+-|bash\s+-c|cmd\s+/c)",  # Command execution
            r"(\$\(.*\)|\`.*\`)",  # Command substitution
        ],
        'XXE': [
            r"(<!ENTITY|<!DOCTYPE|SYSTEM|PUBLIC)",  # XML Entity
        ],
        'CSRF': [
            r"(action=|src=|href=)['\"]?([a-zA-Z0-9\-_.~:/?#@!$&'()*+,;=]+)",  # URL manipulation
        ],
    }

    @staticmethod
    def detect_attacks(data):
        """Analyse les données et retourne les attaques détectées"""
        if not data:
            return {}

        # On convertit en string si c'est un dict
        if isinstance(data, dict):
            data = json.dumps(data)

        data_str = str(data).lower()
        detected = {}

        for attack_type, patterns in OWASPDetector.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    if attack_type not in detected:
                        detected[attack_type] = []
                    detected[attack_type].append(pattern)

        return detected

    @staticmethod
    def detect_scanner(user_agent):
        """Détecte les scanners/bots connus"""
        scanners = [
            'nmap', 'masscan', 'shodan', 'zap', 'nikto', 'burp', 'arachni',
            'sqlmap', 'dirbuster', 'gobuster', 'wpscan', 'joomscan',
            'nuclei', 'metasploit', 'acunetix', 'appscan', 'nessus'
        ]

        if user_agent:
            ua_lower = user_agent.lower()
            for scanner in scanners:
                if scanner in ua_lower:
                    return scanner

        return None

class OWASPHoneypot:
    """Honeypot app fake avec endpoints vulnérables"""

    def __init__(self, logger):
        self.logger = logger
        self.failed_attempts = {}  # IP -> count

    def check_login_attempts(self, ip):
        """Vérifie si l'IP a dépassé les 3 tentatives"""
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = 0

        self.failed_attempts[ip] += 1
        return self.failed_attempts[ip] >= 3

    def generate_fake_app(self):
        """Génère une fausse app web avec endpoints vulnérables"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard v2.5.1</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; margin: 0; }
        .navbar { background: #333; color: white; padding: 10px; }
        .navbar a { color: white; margin: 10px; }
        .content { padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="navbar">
        <h3>Admin Dashboard v2.5.1</h3>
        <a href="/profile">Profile</a>
        <a href="/search">Search</a>
        <a href="/file">Files</a>
        <a href="/api">API</a>
        <a href="/logout">Logout</a>
    </div>
    
    <div class="content">
        <div class="card">
            <h3>Profile Lookup</h3>
            <form action="/profile" method="GET">
                <input name="user_id" placeholder="Enter User ID" required>
                <input type="submit" value="Search">
            </form>
        </div>
        
        <div class="card">
            <h3>Search Users</h3>
            <form action="/search" method="POST">
                <input name="q" placeholder="Search query">
                <input type="submit" value="Search">
            </form>
        </div>
        
        <div class="card">
            <h3>File Manager</h3>
            <form action="/file" method="GET">
                <input name="path" placeholder="File path" value="/var/www/html">
                <input type="submit" value="Browse">
            </form>
        </div>
        
        <div class="card">
            <h3>API Endpoint</h3>
            <form action="/api" method="GET">
                <input name="url" placeholder="https://example.com/api">
                <input type="submit" value="Fetch">
            </form>
        </div>
    </div>
</body>
</html>
"""

    def process_vulnerable_endpoint(self, endpoint, params, ip, user_agent):
        """Traite les endpoints vulnérables et détecte les attaques"""
        detector = OWASPDetector()
        attacks = {}

        # Détecte le scanner
        scanner = detector.detect_scanner(user_agent)

        # Analyse tous les paramètres
        if isinstance(params, dict):
            for key, value in params.items():
                detected = detector.detect_attacks(value)
                if detected:
                    attacks.update(detected)
        else:
            detected = detector.detect_attacks(params)
            if detected:
                attacks.update(detected)

        # Log les attaques
        if attacks:
            attack_str = json.dumps(attacks)
            self.logger.log_attempt(
                ip,
                "HTTP_ATTACK",
                f"SCAN:{scanner or 'UNKNOWN'}",
                endpoint,
                "ATTACK",
                attack_str,
                user_agent
            )
            print(f"[!!!] ATTACK DETECTED from {ip} ({scanner}): {attacks}")

        return attacks

