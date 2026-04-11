<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>AttackMyLure | OSINT Central</title>
    <style>
        :root {
            --bg: #050505;
            --card: #0d0d0d;
            --neon-green: #00ff41;
            --neon-blue: #00f7ff;
            --neon-red: #ff3333;
            --text: #ffffff;
            --border: #222;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background-color: var(--bg);
            background-image:
                linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            color: var(--text);
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 60px;
        }

        .header h1 {
            font-size: 3.5em;
            color: var(--neon-green);
            text-transform: uppercase;
            letter-spacing: 10px;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(0, 255, 65, 0.8);
        }

        .header p {
            color: var(--neon-blue);
            font-size: 1.2em;
            margin-bottom: 5px;
        }

        .header .subtitle {
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
            border-top: 1px solid var(--border);
            padding-top: 10px;
        }

        .dashboards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            max-width: 900px;
            margin-bottom: 40px;
        }

        .dashboard-card {
            background: var(--card);
            border: 2px solid var(--border);
            border-radius: 4px;
            padding: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .dashboard-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-green), transparent);
            animation: scan 3s infinite;
        }

        @keyframes scan {
            0% { left: -100%; }
            50% { left: 100%; }
            100% { left: 100%; }
        }

        .dashboard-card:hover {
            border-color: var(--neon-green);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
            transform: translateY(-5px);
        }

        .dashboard-card.red::before {
            background: linear-gradient(90deg, transparent, var(--neon-red), transparent);
        }

        .dashboard-card.red:hover {
            border-color: var(--neon-red);
            box-shadow: 0 0 20px rgba(255, 51, 51, 0.4);
        }

        .card-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .card-title {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .dashboard-card:hover .card-title {
            color: var(--neon-green);
        }

        .dashboard-card.red:hover .card-title {
            color: var(--neon-red);
        }

        .card-description {
            color: #999;
            font-size: 0.95em;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .card-features {
            list-style: none;
            font-size: 0.85em;
            color: #777;
            margin-bottom: 20px;
        }

        .card-features li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }

        .card-features li::before {
            content: "▸";
            position: absolute;
            left: 0;
            color: var(--neon-green);
        }

        .dashboard-card.red .card-features li::before {
            color: var(--neon-red);
        }

        .card-link {
            display: inline-block;
            padding: 12px 25px;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            text-decoration: none;
            border-radius: 3px;
            transition: all 0.3s;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .dashboard-card:hover .card-link {
            background: var(--neon-green);
            color: var(--bg);
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .dashboard-card.red .card-link {
            background: rgba(255, 51, 51, 0.1);
            border-color: var(--neon-red);
            color: var(--neon-red);
        }

        .dashboard-card.red:hover .card-link {
            background: var(--neon-red);
            color: var(--bg);
            box-shadow: 0 0 10px rgba(255, 51, 51, 0.5);
        }

        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid var(--border);
        }

        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(0, 255, 65, 0.05);
            border: 1px solid rgba(0, 255, 65, 0.2);
            border-radius: 3px;
        }

        .stat-number {
            font-size: 1.8em;
            color: var(--neon-green);
            font-weight: bold;
        }

        .stat-label {
            color: #888;
            font-size: 0.8em;
            margin-top: 5px;
        }

        .footer {
            text-align: center;
            color: #555;
            font-size: 0.85em;
            margin-top: auto;
            border-top: 1px solid var(--border);
            padding-top: 20px;
        }

        .footer a {
            color: var(--neon-blue);
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="header">
    <h1>🍯 ATTACKMYLURE</h1>
    <p>Multi-Protocol Honeypot Intelligence Platform</p>
    <div class="subtitle">
        ➜ Real-time Attack Detection & Analysis
    </div>
</div>

<div class="dashboards">
    <!-- SSH & Commands Dashboard -->
    <div class="dashboard-card">
        <div class="card-icon">🔐</div>
        <div class="card-title">SSH & Commands</div>
        <p class="card-description">
            Analyse des attaques SSH et des commandes exécutées sur le honeypot
        </p>
        <ul class="card-features">
            <li>Top 10 Commandes Exécutées</li>
            <li>Distribution par Protocole</li>
            <li>Timeline 24H des Attaques</li>
            <li>Top Usernames Tentés</li>
            <li>Heatmap Mondiale</li>
            <li>Payloads Capturés</li>
        </ul>
        <a href="index.php" class="card-link">Accéder au Dashboard →</a>
    </div>

    <!-- OWASP Threats Dashboard -->
    <div class="dashboard-card red">
        <div class="card-icon">⚠️</div>
        <div class="card-title">OWASP Web Threats</div>
        <p class="card-description">
            Détection et analyse des vulnérabilités web (SQLi, XSS, LFI, SSRF, etc.)
        </p>
        <ul class="card-features">
            <li>Top Types d'Attaques OWASP</li>
            <li>Endpoints Attaqués</li>
            <li>Méthodes HTTP (GET/POST)</li>
            <li>Scanners Détectés</li>
            <li>Timeline des Menaces</li>
            <li>Alertes Temps Réel</li>
        </ul>
        <a href="threats.php" class="card-link">Accéder au Dashboard →</a>
    </div>
</div>

<div class="stats-row">
    <div class="stat-item">
        <div class="stat-number" id="total-attacks">0</div>
        <div class="stat-label">Attaques Totales</div>
    </div>
    <div class="stat-item">
        <div class="stat-number" id="unique-ips">0</div>
        <div class="stat-label">IPs Uniques</div>
    </div>
    <div class="stat-item">
        <div class="stat-number" id="countries-count">0</div>
        <div class="stat-label">Pays Impliqués</div>
    </div>
    <div class="stat-item">
        <div class="stat-number" id="uptime">24H</div>
        <div class="stat-label">Uptime</div>
    </div>
</div>

<div class="footer">
    <p>AttackMyLure v2.0 | Honeypot Intelligence Platform</p>
    <p>Created by <a href="#">Chrollo0001</a> | 2026</p>
</div>

<script>
    // Récupère les stats globales
    fetch('api.php')
        .then(res => res.json())
        .then(data => {
            if (data.commands) {
                // Total attacks
                const total = (data.commands?.reduce((a, b) => a + b.total, 0) || 0) +
                              (data.protocols?.reduce((a, b) => a + b.total, 0) || 0);
                document.getElementById('total-attacks').textContent = total;

                // Countries
                document.getElementById('countries-count').textContent =
                    data.countries?.length || '5+';
            }
        });
</script>

</body>
</html>

