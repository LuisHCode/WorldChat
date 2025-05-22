<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/conexion.php';

try {
    // Suponiendo que usas un contenedor tipo PHP-DI
    $db = $container->get('base_datos');
    echo "Conexión exitosa a la base de datos.";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
