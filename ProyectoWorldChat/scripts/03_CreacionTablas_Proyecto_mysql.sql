-- Estructura de tablas adaptada a MySQL para replicar datos binarios desde SQL Server
CREATE DATABASE IF NOT EXISTS ProyectoBD;
USE ProyectoBD;

CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasenna VARBINARY(4096) NOT NULL, -- hash SHA-256 como binario
    foto_perfil VARCHAR(255),
    estado VARCHAR(20),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_ingreso DATETIME
);

CREATE TABLE Chat (
    id_chat INT AUTO_INCREMENT PRIMARY KEY,
    nombre_chat VARCHAR(100) NOT NULL,
    id_creador INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_creador) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Participante (
    id_participante INT AUTO_INCREMENT PRIMARY KEY,
    id_chat INT NOT NULL,
    id_usuario INT NOT NULL,
    rol VARCHAR(20),
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Mensaje (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    id_emisor INT NOT NULL,
    id_receptor INT DEFAULT NULL,
    id_chat INT DEFAULT NULL,
    contenido VARBINARY(4096) NOT NULL, -- contenido cifrado como binario
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado_envio VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_emisor) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_receptor) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat)
);
