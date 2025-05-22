<?php
namespace App\controllers;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

use Slim\Routing\RouteCollectorProxy;

$app->get('/', function (Request $request, Response $response, $args) {
    $response->getBody()->write("Bienvenido al Servidor de Negocios");
    return $response;
});

$app->group('/api', function (RouteCollectorProxy $api) {
    $api->group('/artefacto', function (RouteCollectorProxy $artefacto) {
        $artefacto->get('/read[/{id}]', Artefacto::class . ':read');
        $artefacto->post('', Artefacto::class . ':create');
        $artefacto->put('/{id}', Artefacto::class . ':update');
        $artefacto->delete('/{id}', Artefacto::class . ':delete');
        $artefacto->get('/filtrar/{pag}/{lim}', Artefacto::class . ':filtrar');
    });
});

$app->group('/api', function (RouteCollectorProxy $api) {
    $api->group('/cliente', function (RouteCollectorProxy $cliente) {
        $cliente->get('/read[/{id}]', Cliente::class . ':read');
        $cliente->post('', Cliente::class . ':create');
        $cliente->put('/{id}', Cliente::class . ':update');
        $cliente->delete('/{id}', Cliente::class . ':delete');
        $cliente->get('/filtrar/{pag}/{lim}', Cliente::class . ':filtrar');
    });
});    
$app->group('/api', function (RouteCollectorProxy $api) {
    $api->group('/administrador', function (RouteCollectorProxy $administrador) {
        $administrador->get('/read[/{id}]', Administrador::class . ':read');
        $administrador->post('', Administrador::class . ':create');
        $administrador->put('/{id}', Administrador::class . ':update');
        $administrador->delete('/{id}', Administrador::class . ':delete');
        $administrador->get('/filtrar/{pag}/{lim}', Administrador::class . ':filtrar');
    });
});


