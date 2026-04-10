<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>AttackMyLure | OSINT Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #050505;
            --card: #0d0d0d;
            --neon-green: #00ff41;
            --neon-blue: #00f7ff;
            --text: #ffffff;
            --border: #222;
        }

        body {
            background-color: var(--bg);
            background-image: linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            color: var(--text);
            font-family: 'Courier New', monospace;
            margin: 0; padding: 20px;
        }

        .header {
            text-align: center; padding: 20px; border: 1px solid var(--neon-green);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.4); margin-bottom: 30px; background: rgba(0,0,0,0.9);
        }

        .header h1 { margin: 0; color: var(--neon-green); text-transform: uppercase; letter-spacing: 5px; font-size: 2em; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; max-width: 1400px; margin: auto; }

        .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; position: relative; }
        .card::before { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: var(--neon-blue); opacity: 0.5; }

        h2 { color: var(--neon-blue); font-size: 1em; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }

        #payloadList {
            background: #000; padding: 15px; border-radius: 4px; border: 1px inset #222;
            max-height: 250px; overflow-y: auto; font-size: 0.85em; line-height: 1.6;
        }
        .loot-item { border-bottom: 1px solid #111; padding: 5px 0; font-family: 'Courier New', monospace; }
        .loot-date { color: #555; margin-right: 10px; }
        .loot-name { color: var(--neon-green); }

        .alert-item { border-bottom: 1px solid #111; padding: 3px 0; font-family: 'Courier New', monospace; margin: 2px 0; }
        .alert-time { color: #00f7ff; font-weight: bold; margin-right: 5px; }
        .alert-location { color: var(--neon-green); }
        .alert-cmd { color: #ffaa00; }
    </style>
</head>
<body>

<div class="header">
    <h1>[ ATTACK_MY_LURE ] - THREAT_INTEL</h1>
    <p style="color: #666; font-size: 0.8em;">// SYSTEM STATUS: MONITORING ACTIVE // PORT: 22, 80</p>
</div>

<div class="grid">
    <div class="card">
        <h2>TOP_10_COMMANDS</h2>
        <canvas id="commandsChart"></canvas>
    </div>

    <div class="card">
        <h2>PROTOCOL_DISTRIBUTION</h2>
        <canvas id="protoChart"></canvas>
    </div>

    <div class="card">
        <h2>TOP_CITIES</h2>
        <canvas id="citiesChart"></canvas>
    </div>

    <div class="card" style="grid-column: 1 / -1;">
        <h2>ATTACK_TIMELINE_24H</h2>
        <canvas id="activityChart" height="100"></canvas>
    </div>

    <div class="card" style="grid-column: 1 / -1;">
        <h2>REAL_TIME_ALERTS</h2>
        <div id="realtimeAlerts" style="background: #000; padding: 15px; border-radius: 4px; border: 1px inset #222; max-height: 200px; overflow-y: auto; font-size: 0.85em; line-height: 1.8;">
            <div style="color: #555;">Chargement des alertes...</div>
        </div>
    </div>

    <div class="card" style="grid-column: 1 / -1;">
        <h2>CAPTURED_PAYLOADS_DB (LOOT)</h2>
        <div id="payloadList">CHARGEMENT DES SYSTÈMES...</div>
    </div>
        </div>
    </div>
</div>

<script>
    Chart.defaults.color = '#777';
    Chart.defaults.font.family = "'Courier New', monospace";

    fetch('api.php')
        .then(res => res.json())
        .then(data => {
            console.log("Données reçues :", data); // Pour débugger dans la console (F12)

            // 1. Doughnut Chart - Commandes
            new Chart(document.getElementById('commandsChart'), {
                type: 'doughnut',
                data: {
                    labels: data.commands.map(i => i.command),
                    datasets: [{
                        data: data.commands.map(i => i.total),
                        backgroundColor: ['#00ff41', '#00d436', '#00a92b', '#007e20', '#005315', '#003a0e'],
                        borderColor: '#0d0d0d',
                        borderWidth: 3
                    }]
                },
                options: { plugins: { legend: { position: 'right' } } }
            });

            // 2. Bar Chart - Protocoles
            new Chart(document.getElementById('protoChart'), {
                type: 'bar',
                data: {
                    labels: data.protocols.map(i => i.protocol),
                    datasets: [{
                        label: 'Hits',
                        data: data.protocols.map(i => i.total),
                        backgroundColor: 'rgba(0, 247, 255, 0.4)',
                        borderColor: '#00f7ff',
                        borderWidth: 1
                    }]
                }
            });

            // 2.5. Bar Chart - Villes
            if (data.cities && data.cities.length > 0) {
                new Chart(document.getElementById('citiesChart'), {
                    type: 'bar',
                    data: {
                        labels: data.cities.map(i => i.city),
                        datasets: [{
                            label: 'Attaques',
                            data: data.cities.map(i => i.total),
                            backgroundColor: 'rgba(0, 255, 65, 0.3)',
                            borderColor: '#00ff41',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        scales: { x: { beginAtZero: true } }
                    }
                });
            }

            // 3. Line Chart - Activité
            new Chart(document.getElementById('activityChart'), {
                type: 'line',
                data: {
                    labels: data.activity.map(i => i.heure + ':00'),
                    datasets: [{
                        label: 'Attacks',
                        data: data.activity.map(i => i.total),
                        borderColor: '#00ff41',
                        backgroundColor: 'rgba(0, 255, 65, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#00ff41'
                    }]
                }
            });

            // 4. Liste des Payloads (Loot)
            const list = document.getElementById('payloadList');
            if (data.payloads && data.payloads.length > 0) {
                list.innerHTML = data.payloads.map(p => `
                    <div class="loot-item">
                        <span class="loot-date">[${p.date}]</span>
                        <span class="loot-name">FILE: ${p.name}</span>
                        <span style="color:#444"> | SIZE: ${p.size} </span>
                        <span style="color:var(--neon-blue); float:right; font-weight:bold;">[LOOTED]</span>
                    </div>
                `).join('');
            } else {
                list.innerHTML = "> SYSTEM_SCAN: NO_PAYLOADS_DETECTED";
            }

            // 5. Alertes en temps réel
            const alertsDiv = document.getElementById('realtimeAlerts');
            if (data.latest_attacks && data.latest_attacks.length > 0) {
                alertsDiv.innerHTML = data.latest_attacks.map(attack => {
                    const time = new Date(attack.timestamp).toLocaleTimeString();
                    const cmd = attack.command ? attack.command.substring(0, 50) : "N/A";
                    return `
                        <div class="alert-item">
                            <span class="alert-time">[${time}]</span>
                            <span class="alert-location">ALERT: New entry from ${attack.city} (${attack.country})</span>
                            <span class="alert-cmd"> - ${attack.protocol}: "${cmd}"</span>
                        </div>
                    `;
                }).join('');
            } else {
                alertsDiv.innerHTML = "<div style='color:#555;'>> SYSTEM_SCAN: NO_ATTACKS_DETECTED</div>";
            }
        })
        .catch(err => {
            document.getElementById('payloadList').innerHTML = "ERROR_FETCHING_INTEL";
            console.error(err);
        });

    // Refresh auto des alertes toutes les 5 secondes
    setInterval(() => {
        fetch('api.php')
            .then(res => res.json())
            .then(data => {
                const alertsDiv = document.getElementById('realtimeAlerts');
                if (data.latest_attacks && data.latest_attacks.length > 0) {
                    alertsDiv.innerHTML = data.latest_attacks.map(attack => {
                        const time = new Date(attack.timestamp).toLocaleTimeString();
                        const cmd = attack.command ? attack.command.substring(0, 50) : "N/A";
                        return `
                            <div class="alert-item">
                                <span class="alert-time">[${time}]</span>
                                <span class="alert-location">ALERT: New entry from ${attack.city} (${attack.country})</span>
                                <span class="alert-cmd"> - ${attack.protocol}: "${cmd}"</span>
                            </div>
                        `;
                    }).join('');
                }
            })
            .catch(err => console.error(err));
    }, 5000);

    // Refresh complet toutes les 60 secondes
    setTimeout(() => { location.reload(); }, 60000);
</script>

</body>
</html>