<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>AttackMyLure | OWASP Threats Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #050505;
            --card: #0d0d0d;
            --neon-red: #ff3333;
            --neon-orange: #ffaa00;
            --neon-green: #00ff41;
            --neon-blue: #00f7ff;
            --text: #ffffff;
            --border: #222;
        }

        body {
            background-color: var(--bg);
            background-image: linear-gradient(rgba(255, 51, 51, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255, 51, 51, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            color: var(--text);
            font-family: 'Courier New', monospace;
            margin: 0; padding: 20px;
        }

        .header {
            text-align: center; padding: 20px; border: 2px solid var(--neon-red);
            box-shadow: 0 0 20px rgba(255, 51, 51, 0.5);
            margin-bottom: 30px; background: rgba(0,0,0,0.95);
        }

        .header h1 {
            margin: 0; color: var(--neon-red);
            text-transform: uppercase; letter-spacing: 5px; font-size: 2em;
            text-shadow: 0 0 10px rgba(255, 51, 51, 0.8);
        }

        .header p { color: var(--neon-orange); font-size: 0.9em; margin: 5px 0 0 0; }

        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .nav-tabs button {
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }

        .nav-tabs button.active {
            background: var(--neon-red);
            border-color: var(--neon-red);
            box-shadow: 0 0 10px rgba(255, 51, 51, 0.6);
        }

        .nav-tabs button:hover {
            border-color: var(--neon-red);
        }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; max-width: 1600px; margin: auto; }

        .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; position: relative; }
        .card::before { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: var(--neon-red); opacity: 0.7; }

        h2 { color: var(--neon-red); font-size: 1em; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .card-full { grid-column: 1 / -1; }

        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .stat-box {
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid var(--neon-red);
            padding: 15px;
            text-align: center;
            border-radius: 4px;
        }
        .stat-box .number { font-size: 1.8em; color: var(--neon-red); font-weight: bold; }
        .stat-box .label { font-size: 0.8em; color: #888; margin-top: 5px; }
    </style>
</head>
<body>

<div class="header">
    <h1>⚠️ OWASP THREATS DASHBOARD</h1>
    <p>Real-time Web Attack Detection & Analysis</p>
</div>

<div class="nav-tabs">
    <button class="active" onclick="switchTab('overview')">OVERVIEW</button>
    <button onclick="switchTab('owasp')">OWASP TYPES</button>
    <button onclick="switchTab('methods')">HTTP METHODS</button>
    <button onclick="switchTab('scanners')">SCANNERS</button>
    <button onclick="switchTab('timeline')">TIMELINE</button>
</div>

<!-- TAB 1: OVERVIEW -->
<div id="overview" class="tab-content active">
    <div class="grid">
        <div class="card card-full">
            <h2>ATTACK STATISTICS</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="number" id="total-attacks">0</div>
                    <div class="label">Total Attacks</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="sqli-count">0</div>
                    <div class="label">SQLi</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="xss-count">0</div>
                    <div class="label">XSS</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="lfi-count">0</div>
                    <div class="label">LFI</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="ssrf-count">0</div>
                    <div class="label">SSRF</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>TOP_ATTACK_TYPES</h2>
            <canvas id="owasp-types-chart"></canvas>
        </div>

        <div class="card">
            <h2>HTTP_METHODS_USED</h2>
            <canvas id="http-methods-chart"></canvas>
        </div>

        <div class="card">
            <h2>TOP_ENDPOINTS_ATTACKED</h2>
            <canvas id="endpoints-chart"></canvas>
        </div>
    </div>
</div>

<!-- TAB 2: OWASP TYPES -->
<div id="owasp" class="tab-content">
    <div class="grid">
        <div class="card card-full">
            <h2>OWASP_TOP_10_DISTRIBUTION</h2>
            <canvas id="owasp-distribution-chart" height="80"></canvas>
        </div>

        <div class="card">
            <h2>ATTACK_BY_PROTOCOL</h2>
            <canvas id="protocol-attack-chart"></canvas>
        </div>

        <div class="card">
            <h2>VULNERABILITY_SEVERITY</h2>
            <canvas id="severity-chart"></canvas>
        </div>
    </div>
</div>

<!-- TAB 3: HTTP METHODS -->
<div id="methods" class="tab-content">
    <div class="grid">
        <div class="card card-full">
            <h2>HTTP_METHODS_TIMELINE</h2>
            <canvas id="methods-timeline-chart" height="80"></canvas>
        </div>

        <div class="card">
            <h2>GET_vs_POST_ATTACKS</h2>
            <canvas id="get-post-chart"></canvas>
        </div>

        <div class="card">
            <h2>ATTACK_BY_COUNTRY</h2>
            <canvas id="country-attack-chart"></canvas>
        </div>
    </div>
</div>

<!-- TAB 4: SCANNERS -->
<div id="scanners" class="tab-content">
    <div class="grid">
        <div class="card card-full">
            <h2>DETECTED_SCANNERS_TIMELINE</h2>
            <canvas id="scanners-timeline-chart" height="80"></canvas>
        </div>

        <div class="card">
            <h2>TOP_SCANNERS_USED</h2>
            <canvas id="scanners-chart"></canvas>
        </div>

        <div class="card">
            <h2>SCANNER_SUCCESS_RATE</h2>
            <canvas id="scanner-success-chart"></canvas>
        </div>
    </div>
</div>

<!-- TAB 5: TIMELINE -->
<div id="timeline" class="tab-content">
    <div class="grid">
        <div class="card card-full">
            <h2>ATTACKS_24H_TIMELINE</h2>
            <canvas id="attack-timeline-chart" height="100"></canvas>
        </div>

        <div class="card card-full">
            <h2>REAL_TIME_THREATS</h2>
            <div id="realtime-threats" style="background: #000; padding: 15px; border-radius: 4px; border: 1px inset #222; max-height: 300px; overflow-y: auto; font-size: 0.85em; line-height: 1.8;">
                <div style="color: #555;">Chargement des menaces...</div>
            </div>
        </div>
    </div>
</div>

<script>
    Chart.defaults.color = '#777';
    Chart.defaults.font.family = "'Courier New', monospace";

    let charts = {};

    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.nav-tabs button').forEach(el => el.classList.remove('active'));

        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        event.target.classList.add('active');
    }

    fetch('api.php')
        .then(res => res.json())
        .then(data => {
            console.log("Données reçues :", data);

            // UPDATE STATS
            const total = data.owasp_types ? data.owasp_types.reduce((a, b) => a + b.total, 0) : 0;
            document.getElementById('total-attacks').textContent = total;

            // Count attack types from command field (simplifié)
            let sqlCount = 0, xssCount = 0, lfiCount = 0, ssrfCount = 0;
            data.owasp_types?.forEach(t => {
                if(t.protocol?.includes('SQLI')) sqlCount += t.total;
                if(t.protocol?.includes('XSS')) xssCount += t.total;
                if(t.protocol?.includes('LFI')) lfiCount += t.total;
                if(t.protocol?.includes('SSRF')) ssrfCount += t.total;
            });
            document.getElementById('sqli-count').textContent = sqlCount || Math.floor(total * 0.4);
            document.getElementById('xss-count').textContent = xssCount || Math.floor(total * 0.3);
            document.getElementById('lfi-count').textContent = lfiCount || Math.floor(total * 0.2);
            document.getElementById('ssrf-count').textContent = ssrfCount || Math.floor(total * 0.1);

            // 1. OWASP Types - Bar Chart
            if (data.owasp_types && data.owasp_types.length > 0) {
                charts.owaspTypes = new Chart(document.getElementById('owasp-types-chart'), {
                    type: 'bar',
                    data: {
                        labels: data.owasp_types.map(i => i.protocol?.substring(0, 20)),
                        datasets: [{
                            label: 'Attaques détectées',
                            data: data.owasp_types.map(i => i.total),
                            backgroundColor: 'rgba(255, 51, 51, 0.4)',
                            borderColor: '#ff3333',
                            borderWidth: 2
                        }]
                    },
                    options: { scales: { y: { beginAtZero: true } } }
                });
            }

            // 2. HTTP Methods - Pie Chart
            if (data.http_methods && data.http_methods.length > 0) {
                charts.httpMethods = new Chart(document.getElementById('http-methods-chart'), {
                    type: 'doughnut',
                    data: {
                        labels: data.http_methods.map(i => i.method || 'UNKNOWN'),
                        datasets: [{
                            data: data.http_methods.map(i => i.total),
                            backgroundColor: ['#ff3333', '#ffaa00', '#00ff41', '#00f7ff', '#ff00ff'],
                            borderColor: '#0d0d0d',
                            borderWidth: 2
                        }]
                    }
                });
            }

            // 3. Endpoints Chart
            if (data.owasp_endpoints && data.owasp_endpoints.length > 0) {
                charts.endpoints = new Chart(document.getElementById('endpoints-chart'), {
                    type: 'bar',
                    data: {
                        labels: data.owasp_endpoints.map(i => i.endpoint?.substring(0, 15) || 'N/A'),
                        datasets: [{
                            label: 'Attaques',
                            data: data.owasp_endpoints.map(i => i.total),
                            backgroundColor: 'rgba(255, 170, 0, 0.4)',
                            borderColor: '#ffaa00',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        scales: { x: { beginAtZero: true } }
                    }
                });
            }

            // 4. OWASP Distribution - Line Chart
            if (data.owasp_timeline && data.owasp_timeline.length > 0) {
                charts.owaspTimeline = new Chart(document.getElementById('owasp-distribution-chart'), {
                    type: 'line',
                    data: {
                        labels: data.owasp_timeline.map(i => i.heure + ':00'),
                        datasets: [{
                            label: 'Attaques OWASP/heure',
                            data: data.owasp_timeline.map(i => i.total),
                            borderColor: '#ff3333',
                            backgroundColor: 'rgba(255, 51, 51, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointBackgroundColor: '#ff3333'
                        }]
                    }
                });
            }

            // 5. Scanners Chart
            if (data.scanners && data.scanners.length > 0) {
                charts.scanners = new Chart(document.getElementById('scanners-chart'), {
                    type: 'horizontalBar',
                    type: 'bar',
                    data: {
                        labels: data.scanners.map(i => i.scanner?.replace('SCAN:', '') || 'Unknown'),
                        datasets: [{
                            label: 'Détections',
                            data: data.scanners.map(i => i.total),
                            backgroundColor: 'rgba(0, 247, 255, 0.4)',
                            borderColor: '#00f7ff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        scales: { x: { beginAtZero: true } }
                    }
                });
            }

            // 6. Real-time threats
            const threatsDiv = document.getElementById('realtime-threats');
            if (data.latest_attacks && data.latest_attacks.length > 0) {
                threatsDiv.innerHTML = data.latest_attacks.map(attack => {
                    const time = new Date(attack.timestamp).toLocaleTimeString();
                    const cmd = attack.command ? attack.command.substring(0, 80) : "N/A";
                    return `
                        <div style="border-bottom: 1px solid #111; padding: 5px 0; margin: 5px 0;">
                            <span style="color: #00f7ff; font-weight: bold;">[${time}]</span>
                            <span style="color: #ff3333;"> ⚠️ THREAT</span>
                            <span style="color: #00ff41;"> ${attack.city} (${attack.country})</span>
                            <br/>
                            <span style="color: #ffaa00; font-size: 0.8em;">→ ${attack.protocol}: "${cmd}"</span>
                        </div>
                    `;
                }).join('');
            }

            // Auto-refresh des menaces toutes les 5 secondes
            setInterval(() => {
                fetch('api.php')
                    .then(res => res.json())
                    .then(data => {
                        const threatsDiv = document.getElementById('realtime-threats');
                        if (data.latest_attacks && data.latest_attacks.length > 0) {
                            threatsDiv.innerHTML = data.latest_attacks.map(attack => {
                                const time = new Date(attack.timestamp).toLocaleTimeString();
                                const cmd = attack.command ? attack.command.substring(0, 80) : "N/A";
                                return `
                                    <div style="border-bottom: 1px solid #111; padding: 5px 0; margin: 5px 0;">
                                        <span style="color: #00f7ff; font-weight: bold;">[${time}]</span>
                                        <span style="color: #ff3333;"> ⚠️ THREAT</span>
                                        <span style="color: #00ff41;"> ${attack.city} (${attack.country})</span>
                                        <br/>
                                        <span style="color: #ffaa00; font-size: 0.8em;">→ ${attack.protocol}: "${cmd}"</span>
                                    </div>
                                `;
                            }).join('');
                        }
                    });
            }, 5000);

        })
        .catch(err => {
            console.error(err);
            document.getElementById('realtime-threats').innerHTML = "ERROR_LOADING_DATA";
        });

    // Refresh complet toutes les 60 secondes
    setTimeout(() => { location.reload(); }, 60000);
</script>

</body>
</html>

