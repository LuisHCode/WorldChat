<?php
namespace App\controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Container\ContainerInterface;

use PDO;

class Usuario
{
    protected $container;

    public function __construct(ContainerInterface $c)
    {
        $this->container = $c;
    }

    public function create(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);

        $sql = "EXEC sp_CrearUsuario @nombre_usuario = :nombre_usuario, @nombre_completo = :nombre_completo, @telefono = :telefono, @correo = :correo, @contrasenna = :contrasenna, @foto_perfil = :foto_perfil, @estado = :estado";

        $con = $this->container->get('base_datos');
        $con->beginTransaction();
        $query = $con->prepare($sql);

        $query->bindValue(':nombre_usuario', $body['nombre_usuario'] ?? null, PDO::PARAM_STR);
        $query->bindValue(':nombre_completo', $body['nombre_completo'] ?? null, PDO::PARAM_STR);
        $query->bindValue(':telefono', $body['telefono'] ?? null, PDO::PARAM_STR);
        $query->bindValue(':correo', $body['correo'] ?? null, PDO::PARAM_STR);
        $query->bindValue(':contrasenna', $body['contrasenna'], PDO::PARAM_STR);
        $query->bindValue(':foto_perfil', $body['foto_perfil'] ?? null, PDO::PARAM_STR);
        $query->bindValue(':estado', $body['estado'] ?? 'Activo', PDO::PARAM_STR);

        try {
            $query->execute();
            $con->commit();
            $status = 201;
        } catch (\PDOException $e) {
            $status = 500;
            $con->rollBack();
            var_dump($e->getMessage());
            die();
        }

        $query = null;
        $con = null;

        return $response->withStatus($status);
    }

}