<?php
namespace App\controllers;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

use Slim\Routing\RouteCollectorProxy;

$app->get('/', function (Request $request, Response $response, $args) {
    $response->getBody()->write("Hola Mundo!");
    return $response;
});

$app->group('/api', function (RouteCollectorProxy $api) {
    $api->group('/usuario', function (RouteCollectorProxy $endpoint) {
        $endpoint->get('/read', Usuario::class . ':read');
        $endpoint->post('', Usuario::class . ':create');
        $endpoint->put('/{id}', Usuario::class . ':update');
        $endpoint->delete('/{id}', Usuario::class . ':delete');
        $endpoint->get('/filtrar/{pag}/{lim}', Usuario::class . ':filtrar');
    });

    $api->group('/mensaje', function (RouteCollectorProxy $endpoint) {
        $endpoint->get('/read', Mensaje::class . ':readPrivate');
        $endpoint->get('/read/chat/{id_chat}', Mensaje::class . ':readChat');
        $endpoint->post('/{id_receptor}', Mensaje::class . ':sendPrivateMessage');
        $endpoint->post('/group/{id_chat}', Mensaje::class . ':sendChatMessage');
        $endpoint->delete('/{id}', Mensaje::class . ':delete');
        $endpoint->get('/filtrar/{pag}/{lim}', Mensaje::class . ':filtrar');
    });

     $api->group('/chat', function (RouteCollectorProxy $endpoint) {
        $endpoint->POST('', Chat::class . ':create');
    });

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
