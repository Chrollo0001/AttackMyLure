<?php
header('Content-Type: application/json');

$host = 'localhost';
$dbname = 'attack_my_lure';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Vérifier les données dans la base
    $stmt = $pdo->query("SELECT protocol, COUNT(*) as count FROM attacks GROUP BY protocol");
    $protocols = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $stmt = $pdo->query("SELECT COUNT(*) as total FROM attacks WHERE protocol = 'HTTP_ATTACK'");
    $http_attack_count = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    $stmt = $pdo->query("SELECT * FROM attacks WHERE protocol = 'HTTP_ATTACK' LIMIT 5");
    $samples = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode([
        'protocols_count' => $protocols,
        'http_attack_total' => $http_attack_count,
        'sample_records' => $samples
    ], JSON_PRETTY_PRINT);

} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>

