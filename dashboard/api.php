<?php
header('Content-Type: application/json');

$host = 'localhost';
$dbname = 'attack_my_lure';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // 1. TOP COMMANDES
    $stmt = $pdo->query("SELECT command, COUNT(*) as total FROM attacks WHERE protocol = 'COMMAND' AND command != '' GROUP BY command ORDER BY total DESC LIMIT 10");
    $commands = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 2. ACTIVITÉ
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, COUNT(*) as total FROM attacks WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure ORDER BY heure ASC");
    $activity = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 3. PROTOCOLES
    $stmt = $pdo->query("SELECT protocol, COUNT(*) as total FROM attacks GROUP BY protocol");
    $protocols = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 4. VILLES (Graphique en colonnes)
    $stmt = $pdo->query("SELECT city, COUNT(*) as total FROM attacks WHERE city != 'Unknown' GROUP BY city ORDER BY total DESC LIMIT 15");
    $cities = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 5. 5 DERNIÈRES ATTAQUES EN TEMPS RÉEL
    $stmt = $pdo->query("SELECT timestamp, ip_address, country, city, command, protocol FROM attacks ORDER BY timestamp DESC LIMIT 5");
    $latest_attacks = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 4. PAYLOADS (Chemin sécurisé)
    // Le chemin absolu vers le projet AttackMyLure
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

    echo json_encode(['commands' => $commands, 'activity' => $activity, 'protocols' => $protocols, 'payloads' => $payloads, 'cities' => $cities, 'latest_attacks' => $latest_attacks]);
} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}