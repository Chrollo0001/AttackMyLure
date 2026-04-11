<?php
header('Content-Type: application/json');

$host = 'localhost';
$dbname = 'attack_my_lure';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // ===== OVERVIEW TAB =====
    // 1. TOTAL ATTACKS OWASP
    $stmt = $pdo->query("SELECT COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK'");
    $total_owasp = $stmt->fetch(PDO::FETCH_ASSOC)['total'] ?? 0;

    // 2. TOP ATTACK TYPES (SQLI, XSS, LFI, SSRF, etc.)
    $stmt = $pdo->query("SELECT attack_type, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND attack_type IS NOT NULL AND attack_type != '' GROUP BY attack_type ORDER BY total DESC LIMIT 10");
    $owasp_types = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 3. HTTP METHODS (GET vs POST)
    $stmt = $pdo->query("SELECT http_method, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND http_method IS NOT NULL AND http_method != '' GROUP BY http_method ORDER BY total DESC");
    $http_methods = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 4. TOP ENDPOINTS ATTACKED
    $stmt = $pdo->query("SELECT endpoint, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND endpoint IS NOT NULL AND endpoint != '' GROUP BY endpoint ORDER BY total DESC LIMIT 10");
    $endpoints = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // ===== OWASP TYPES TAB =====
    // 5. OWASP DISTRIBUTION TIMELINE (by hour)
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure ORDER BY heure ASC");
    $owasp_timeline = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 6. ATTACK BY PROTOCOL (HTTP_ATTACK distribution by type)
    $stmt = $pdo->query("SELECT attack_type, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND attack_type IS NOT NULL GROUP BY attack_type");
    $protocol_attack = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // ===== HTTP METHODS TAB =====
    // 7. HTTP METHODS TIMELINE
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, http_method, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND http_method IS NOT NULL AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure, http_method ORDER BY heure ASC");
    $methods_timeline = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 8. GET vs POST Chart
    $stmt = $pdo->query("SELECT http_method, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND http_method IN ('GET', 'POST') GROUP BY http_method");
    $get_post = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 9. ATTACK BY COUNTRY (HTTP only)
    $stmt = $pdo->query("SELECT country, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND country != 'Unknown' GROUP BY country ORDER BY total DESC LIMIT 10");
    $country_attack = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // ===== SCANNERS TAB =====
    // 10. SCANNERS TIMELINE
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, scanner_name, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND scanner_name IS NOT NULL AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure, scanner_name ORDER BY heure ASC");
    $scanners_timeline = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 11. TOP SCANNERS
    $stmt = $pdo->query("SELECT scanner_name, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND scanner_name IS NOT NULL AND scanner_name != '' GROUP BY scanner_name ORDER BY total DESC LIMIT 10");
    $scanners = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // ===== TIMELINE TAB =====
    // 12. ATTACKS 24H TIMELINE
    $stmt = $pdo->query("SELECT HOUR(timestamp) as heure, COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK' AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) GROUP BY heure ORDER BY heure ASC");
    $attack_timeline_24h = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 13. LATEST ATTACKS (Real-time threats)
    $stmt = $pdo->query("SELECT timestamp, ip_address, country, city, endpoint, attack_type, payload, http_method, scanner_name FROM attacks WHERE protocol = 'HTTP_ATTACK' ORDER BY timestamp DESC LIMIT 5");
    $latest_attacks = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Return all data
    echo json_encode([
        'total_attacks' => $total_owasp,
        'owasp_types' => $owasp_types,
        'http_methods' => $http_methods,
        'endpoints' => $endpoints,
        'owasp_timeline' => $owasp_timeline,
        'protocol_attack' => $protocol_attack,
        'methods_timeline' => $methods_timeline,
        'get_post' => $get_post,
        'country_attack' => $country_attack,
        'scanners_timeline' => $scanners_timeline,
        'scanners' => $scanners,
        'attack_timeline_24h' => $attack_timeline_24h,
        'latest_attacks' => $latest_attacks
    ]);

} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>

