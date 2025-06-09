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


    public function sendChatMessage(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);
        // Convertir cadenas vacías a null
        foreach ($body as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $body[$k] = null;
            }
        }

        $id_chat = isset($args['id_chat']) ? (int) $args['id_chat'] : null;

        // Validar parámetros
        if (empty($body['id_emisor']) || empty($id_chat) || empty($body['contenido'])) {
            $response->getBody()->write(json_encode(['error' => 'Faltan parámetros obligatorios']));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        $sql = "EXEC sp_EnviarMensaje @id_emisor = :id_emisor, @id_chat = :id_chat, @contenido = :contenido";
        $con = $this->container->get('base_datos');
        $query = $con->prepare($sql);

        $query->bindValue(':id_emisor', $body['id_emisor'], PDO::PARAM_INT);
        $query->bindValue(':id_chat', $id_chat, PDO::PARAM_INT);
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

    public function readPrivate(Request $request, Response $response, $args)
    {
        $body = json_decode($request->getBody(), true);

        foreach ($body as $k => $v) {
            if (is_string($v) && trim($v) === "") {
                $body[$k] = null;
            }
        }
        $sql = "EXEC sp_ObtenerMensajesPrivados @id_usuario1 = :id_usuario1, @id_usuario2 = :id_usuario2";
        $con = $this->container->get('base_datos');
        $con->beginTransaction();
        $query = $con->prepare($sql);

        $query->bindValue(':id_usuario1', $body['id_usuario1'] ?? null, PDO::PARAM_INT);
        $query->bindValue(':id_usuario2', $body['id_usuario2'] ?? null, PDO::PARAM_INT);
        $query->execute();
        $res = $query->fetchAll(PDO::FETCH_ASSOC);
        try {
            $query->execute();
            $con->commit();
            $status = 201;
        } catch (\PDOException $e) {
            $status = 500;
            $con->rollBack();
        }
        $query = null;
        $con = null;

        $response->getBody()->write(json_encode($res ?? [], JSON_UNESCAPED_UNICODE));
        return $response
            ->withHeader('Content-Type', 'application/json')
            ->withStatus($status);
    }

    public function readChat(Request $request, Response $response, $args)
    {
        $id_chat = isset($args['id_chat']) ? (int) $args['id_chat'] : null;
        $sql = "EXEC sp_LeerMensajesChat @id_chat = :id_chat";
        $con = $this->container->get('base_datos');
        $con->beginTransaction();
        $query = $con->prepare($sql);

        if (empty($id_chat)) {
            $response->getBody()->write(json_encode(['error' => 'Faltan parámetros obligatorios']));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        $query->bindValue(':id_chat', $id_chat, PDO::PARAM_INT);
        $query->execute();
        $res = $query->fetchAll(PDO::FETCH_ASSOC);
        try {
            $query->execute();
            $con->commit();
            $status = 201;
        } catch (\PDOException $e) {
            $status = 500;
            $con->rollBack();
        }
        $query = null;
        $con = null;

        $response->getBody()->write(json_encode($res ?? [], JSON_UNESCAPED_UNICODE));
        return $response
            ->withHeader('Content-Type', 'application/json')
            ->withStatus($status);
    }


}