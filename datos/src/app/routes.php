<?php
    namespace App\controllers;
    use Psr\Http\Message\ResponseInterface as Response;
    use Psr\Http\Message\ServerRequestInterface as Request;

    use Slim\Routing\RouteCollectorProxy;

    $app->get('/', function (Request $request, Response $response, $args) {
        $response->getBody()->write("Hola Mundo!");
        return $response;
    });

    $app->get('/test-db', function (Request $request, Response $response, $args) {
        global $container;
        try {
            $db = $container->get('base_datos');
            $response->getBody()->write("Conexión exitosa a la base de datos.");
        } catch (\Exception $e) {
            $response->getBody()->write("Error: " . $e->getMessage());
        }
        return $response;
    });
