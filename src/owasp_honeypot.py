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
            'nuclei', 'metasploit', 'acunetix', 'appscan', 'nessus',
            'curl', 'wget', 'python', 'java', 'powershell'
        ]
        
        if user_agent:
            ua_lower = user_agent.lower()
            for scanner in scanners:
                if scanner in ua_lower:
                    return scanner
        
        return "Unknown"

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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Control Panel v3.1</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            width: 280px;
            background: #343a40;
            color: white;
            padding-top: 20px;
        }
        .sidebar .nav-link {
            color: #adb5bd;
            font-size: 1.1em;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            color: #ffffff;
            background-color: #495057;
        }
        .sidebar .sidebar-header {
            padding: 0 20px 20px 20px;
            border-bottom: 1px solid #495057;
        }
        .main-content {
            margin-left: 280px;
            padding: 20px;
        }
        .card-title {
            color: #0d6efd;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h3><i class="fas fa-shield-alt"></i> Admin Panel</h3>
            <small>Version 3.1 - Internal</small>
        </div>
        <ul class="nav flex-column">
            <li class="nav-item"><a class="nav-link active" href="#"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" href="/profile"><i class="fas fa-user"></i> User Profile</a></li>
            <li class="nav-item"><a class="nav-link" href="/search"><i class="fas fa-search"></i> Search Data</a></li>
            <li class="nav-item"><a class="nav-link" href="/file"><i class="fas fa-folder-open"></i> File Explorer</a></li>
            <li class="nav-item"><a class="nav-link" href="/api"><i class="fas fa-cogs"></i> API Control</a></li>
            <li class="nav-item"><a class="nav-link" href="/settings"><i class="fas fa-tools"></i> Settings</a></li>
            <li class="nav-item mt-auto"><a class="nav-link" href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
        </ul>
    </div>

    <div class="main-content">
        <div class="container-fluid">
            <h1 class="mt-4">Dashboard Overview</h1>
            <p class="text-muted">System status and management tools.</p>

            <div class="row">
                <div class="col-lg-8">
                    <!-- Vulnerable Forms Card -->
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-bolt"></i> Quick Actions</div>
                        <div class="card-body">
                            <div class="row">
                                <!-- Profile Lookup -->
                                <div class="col-md-6 mb-3">
                                    <h5 class="card-title">Profile Lookup</h5>
                                    <form action="/profile" method="GET">
                                        <div class="input-group">
                                            <input name="user_id" class="form-control" placeholder="Enter User ID" required>
                                            <button class="btn btn-primary" type="submit">Search</button>
                                        </div>
                                    </form>
                                </div>
                                <!-- Search Users -->
                                <div class="col-md-6 mb-3">
                                    <h5 class="card-title">Search Users</h5>
                                    <form action="/search" method="POST">
                                        <div class="input-group">
                                            <input name="q" class="form-control" placeholder="Search query...">
                                            <button class="btn btn-primary" type="submit">Search</button>
                                        </div>
                                    </form>
                                </div>
                                <!-- File Manager -->
                                <div class="col-md-6 mb-3">
                                    <h5 class="card-title">File Manager</h5>
                                    <form action="/file" method="GET">
                                        <div class="input-group">
                                            <input name="path" class="form-control" value="/var/www/html">
                                            <button class="btn btn-secondary" type="submit">Browse</button>
                                        </div>
                                    </form>
                                </div>
                                <!-- API Endpoint -->
                                <div class="col-md-6 mb-3">
                                    <h5 class="card-title">API Endpoint</h5>
                                    <form action="/api" method="GET">
                                        <div class="input-group">
                                            <input name="url" class="form-control" placeholder="https://example.com/api">
                                            <button class="btn btn-secondary" type="submit">Fetch</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card mb-4">
                        <div class="card-header"><i class="fas fa-chart-line"></i> Server Load</div>
                        <div class="card-body">
                            <canvas id="serverLoadChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Fake chart for credibility
        const ctx = document.getElementById('serverLoadChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['-5min', '-4min', '-3min', '-2min', '-1min', 'Now'],
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: [15, 20, 18, 25, 22, 30],
                    borderColor: 'rgba(0, 123, 255, 0.8)',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    </script>
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

        # Retourne les attaques détectées (le logging se fera dans main.py)
        if attacks:
            print(f"[!!!] ATTACK DETECTED from {ip}: {attacks}")
        
        return attacks

