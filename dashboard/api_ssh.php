<?php
header('Content-Type: application/json');

$host = 'localhost';
$dbname = 'attack_my_lure';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // 1. TOP COMMANDES SSH/SHELL UNIQUEMENT
    $stmt = $pdo->query("SELECT command, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND command IS NOT NULL AND command != '' GROUP BY command ORDER BY total DESC LIMIT 10");
    $commands = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 2. ACTIVITÉ 24H (SSH UNIQUEMENT)
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure ORDER BY heure ASC");
    $activity = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 3. PROTOCOLES SSH/COMMAND
    $stmt = $pdo->query("SELECT protocol, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') GROUP BY protocol");
    $protocols = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 4. VILLES (SSH UNIQUEMENT)
    $stmt = $pdo->query("SELECT city, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND city != 'Unknown' GROUP BY city ORDER BY total DESC LIMIT 15");
    $cities = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 5. 5 DERNIÈRES ATTAQUES SSH EN TEMPS RÉEL
    $stmt = $pdo->query("SELECT timestamp, ip_address, country, city, command, protocol FROM attacks WHERE protocol IN ('COMMAND', 'SSH') ORDER BY timestamp DESC LIMIT 5");
    $latest_attacks = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 6. TOP 10 USERNAMES ATTAQUÉS (SSH UNIQUEMENT)
    $stmt = $pdo->query("SELECT username, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND username IS NOT NULL AND username != '' GROUP BY username ORDER BY total DESC LIMIT 10");
    $usernames = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 7. TOP 10 COMMANDES DANGEREUSES (SSH UNIQUEMENT)
    $stmt = $pdo->query("SELECT command, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND command IS NOT NULL AND command != '' GROUP BY command ORDER BY total DESC LIMIT 10");
    $dangerous_commands = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 8. HEATMAP MONDE (SSH UNIQUEMENT)
    $stmt = $pdo->query("SELECT country, COUNT(*) as total FROM attacks WHERE protocol IN ('COMMAND', 'SSH') AND country != 'Unknown' GROUP BY country ORDER BY total DESC LIMIT 20");
    $countries = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 9. PAYLOADS CAPTURÉS
    $payloadDir = "C:\\Users\\chrol\\Desktop\\AttackMyLure\\src\\captured_payloads";

    $payloads = [];
    if (is_dir($payloadDir)) {
        $files = scandir($payloadDir, SCANDIR_SORT_DESCENDING);
        foreach ($files as $file) {
            if ($file !== '.' && $file !== '..' && is_file($payloadDir.'/'.$file)) {
                $payloads[] = [
                    'name' => $file,
                    'size' => round(filesize($payloadDir.'/'.$file) / 1024, 2) . ' KB',
                    'date' => date("d/m H:i", filemtime($payloadDir.'/'.$file))
                ];
            }
        }
    }

    echo json_encode([
        'commands' => $commands,
        'activity' => $activity,
        'protocols' => $protocols,
        'payloads' => $payloads,
        'cities' => $cities,
        'latest_attacks' => $latest_attacks,
        'usernames' => $usernames,
        'dangerous_commands' => $dangerous_commands,
        'countries' => $countries
    ]);

} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}

