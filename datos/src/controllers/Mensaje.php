<?php
namespace App\controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Container\ContainerInterface;

use PDO;

class Mensaje
{
    protected $container;

    public function __construct(ContainerInterface $c)
    {
        $this->container = $c;
    }

    public function sendPrivateMessage(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);

        // Convertir cadenas vacías a null
        foreach ($body as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $body[$k] = null;
            }
        }

        $id_receptor = isset($args['id_receptor']) ? (int) $args['id_receptor'] : null;

        // Validar parámetros
        if (empty($body['id_emisor']) || empty($id_receptor) || empty($body['contenido'])) {
            $response->getBody()->write(json_encode(['error' => 'Faltan parámetros obligatorios']));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        $sql = "EXEC sp_EnviarMensajePrivado @id_emisor = :id_emisor, @id_receptor = :id_receptor, @contenido = :contenido";
        $con = $this->container->get('base_datos');
        $query = $con->prepare($sql);

        $query->bindValue(':id_emisor', $body['id_emisor'], PDO::PARAM_INT);
        $query->bindValue(':id_receptor', $id_receptor, PDO::PARAM_INT);
        $query->bindValue(':contenido', $body['contenido'], PDO::PARAM_STR);

        try {
            $query->execute();

            // Avanzar hasta encontrar un result set con columnas
            do {
                $columns = $query->columnCount();
                if ($columns > 0) {
                    break;
                }
            } while ($query->nextRowset());

            // Si no hay columnas, error
            if ($columns === 0) {
                throw new Exception("No hay datos para leer.");
            }

            $result = $query->fetch(PDO::FETCH_ASSOC);

            if ($result && isset($result['exito']) && $result['exito'] == 1) {
                $status = 201;
                $response->getBody()->write(json_encode(['mensaje' => 'Mensaje enviado con exito']));
            } else {
                $status = 400;
                $response->getBody()->write(json_encode(['error' => 'No se pudo enviar el mensaje']));
            }
        } catch (\PDOException $e) {
            $status = 500;
            $response->getBody()->write(json_encode(['error' => $e->getMessage()]));
        } catch (\Exception $e) {
            $status = 500;
            $response->getBody()->write(json_encode(['error' => $e->getMessage()]));
        }


        $query = null;
        $con = null;

        return $response->withStatus($status)->withHeader('Content-Type', 'application/json');
    }


    public function update(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);

        // Convertir cadenas vacías a null
        foreach ($body as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $body[$k] = null;
            }
        }
        // Convertir cadenas vacías a null también en $args
        foreach ($args as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $args[$k] = null;
            }
        }

        $sql = "EXEC sp_ModificarUsuario @id_usuario = :id_usuario, @nombre_usuario = :nombre_usuario, @nombre_completo = :nombre_completo, @telefono = :telefono, @correo = :correo, @contrasenna = :contrasenna, @foto_perfil = :foto_perfil, @estado = :estado";

        $con = $this->container->get('base_datos');
        $con->beginTransaction();
        $query = $con->prepare($sql);

        $query->bindValue(':id_usuario', filter_var($args['id'], FILTER_SANITIZE_SPECIAL_CHARS) ?? null, PDO::PARAM_INT);
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
            var_dump($e->getMessage());
            die();
            $status = 500;
            $con->rollBack();
        }

        $query = null;
        $con = null;

        return $response->withStatus($status);
    }

}