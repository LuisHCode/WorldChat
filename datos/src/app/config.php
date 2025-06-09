<?php
$container->set(
    'config_bd',
    function () {
        return (object) [
            "driver" => "sqlsrv",
            "host" => "host.docker.internal",
            "db" => "ProyectoBD",
            "usr" => "usuario",
            "passw" => "usuario",
            "charset" => "utf8mb4",
        ];
    }
);