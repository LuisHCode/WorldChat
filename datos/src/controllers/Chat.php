<?php
namespace App\controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Container\ContainerInterface;

use PDO;

class Chat
{
    protected $container;

    public function __construct(ContainerInterface $c)
    {
        $this->container = $c;
    }

    public function create(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);


        // Convertir cadenas vacías a null
        foreach ($body as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $body[$k] = null;
            }
        }

        // Validar parámetros
        if (empty($body['nombre_chat']) || empty($body['id_creador'])) {
            $response->getBody()->write(json_encode(['error' => 'Faltan parámetros obligatorios']));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        $sql = "EXEC sp_CrearChat @nombre_chat = :nombre_chat, @id_creador = :id_creador";
        $con = $this->container->get('base_datos');
        $query = $con->prepare($sql);

        $query->bindValue(':nombre_chat', $body['nombre_chat'], PDO::PARAM_STR);
        $query->bindValue(':id_creador', $body['id_creador'], PDO::PARAM_INT);
        try {
            $query->execute();
            $status = 201;
        } catch (\PDOException $e) {
            var_dump($e->getMessage());
            $status = 500;
        }

        $query = null;
        $con = null;

        return $response->withStatus($status);
    }

}