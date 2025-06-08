/*
Integrantes:
Steven Alvarado Guzman C30333
Anthony Mora Loaiza C35219
José Luis López Hernandez C34360
*/


CREATE LOGIN usuario WITH PASSWORD = 'usuario';


CREATE DATABASE ProyectoBD
GO 

USE ProyectoBD;
GO

CREATE USER usuario FOR LOGIN usuario;
GO

ALTER ROLE db_datareader ADD MEMBER usuario;  -- Permiso lectura
ALTER ROLE db_datawriter ADD MEMBER usuario;  -- Permiso escritura
GO


CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasenna VARBINARY(MAX) NOT NULL,
    foto_perfil VARCHAR(255),
    estado VARCHAR(20),
    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    ultimo_ingreso DATETIME
)

CREATE TABLE Chat (
    id_chat INT PRIMARY KEY IDENTITY(1,1),
    nombre_chat VARCHAR(100) NOT NULL,
    id_creador INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (id_creador) REFERENCES Usuario(id_usuario)
)

CREATE TABLE Participante (
    id_participante INT PRIMARY KEY IDENTITY(1,1),
    id_chat INT NOT NULL,
    id_usuario INT NOT NULL,
    rol VARCHAR(20),
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
)

CREATE TABLE Mensaje (
    id_mensaje INT PRIMARY KEY IDENTITY(1,1),
    id_emisor INT NOT NULL,
    id_receptor INT NULL,
    id_chat INT NULL,
    contenido VARBINARY(MAX) NOT NULL,
    fecha_envio DATETIME NOT NULL DEFAULT GETDATE(),
    estado_envio VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_emisor) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_receptor) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat)
)