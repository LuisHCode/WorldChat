-- Procedimientos almacenados adaptados a MySQL
USE ProyectoBD;

DELIMITER //

CREATE PROCEDURE sp_CrearUsuario (
    IN nombre_usuario VARCHAR(50),
    IN nombre_completo VARCHAR(100),
    IN telefono VARCHAR(20),
    IN correo VARCHAR(100),
    IN contrasenna VARBINARY(4096),
    IN foto_perfil VARCHAR(255),
    IN estado VARCHAR(20)
)
BEGIN
    IF EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya está en uso';
    END IF;

    IF EXISTS (SELECT 1 FROM Usuario WHERE correo = correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya está registrado';
    END IF;

    IF EXISTS (SELECT 1 FROM Usuario WHERE telefono = telefono) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El número de teléfono ya está registrado';
    END IF;

    INSERT INTO Usuario (nombre_usuario, nombre_completo, telefono, correo, contrasenna, foto_perfil, estado)
    VALUES (nombre_usuario, nombre_completo, telefono, correo, contrasenna, foto_perfil, estado);
END //

CREATE PROCEDURE sp_ModificarUsuario (
    IN id_usuario INT,
    IN nombre_usuario VARCHAR(50),
    IN nombre_completo VARCHAR(100),
    IN telefono VARCHAR(20),
    IN correo VARCHAR(100),
    IN contrasenna VARBINARY(4096),
    IN foto_perfil VARCHAR(255),
    IN estado VARCHAR(20)
)
BEGIN
    UPDATE Usuario SET
        nombre_usuario = COALESCE(nombre_usuario, nombre_usuario),
        nombre_completo = COALESCE(nombre_completo, nombre_completo),
        telefono = COALESCE(telefono, telefono),
        correo = COALESCE(correo, correo),
        contrasenna = COALESCE(contrasenna, contrasenna),
        foto_perfil = COALESCE(foto_perfil, foto_perfil),
        estado = COALESCE(estado, estado)
    WHERE id_usuario = id_usuario;
END //

CREATE PROCEDURE sp_CrearChat (
    IN nombre_chat VARCHAR(100),
    IN id_creador INT
)
BEGIN
    INSERT INTO Chat (nombre_chat, id_creador)
    VALUES (nombre_chat, id_creador);

    INSERT INTO Participante (id_chat, id_usuario, rol)
    VALUES (LAST_INSERT_ID(), id_creador, 'Administrador');
END //

CREATE PROCEDURE sp_AgregarParticipante (
    IN id_chat INT,
    IN id_usuario INT,
    IN rol VARCHAR(20)
)
BEGIN
    IF EXISTS (
        SELECT 1 FROM Participante 
        WHERE id_chat = id_chat AND id_usuario = id_usuario
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario ya es participante del chat';
    END IF;

    INSERT INTO Participante (id_chat, id_usuario, rol)
    VALUES (id_chat, id_usuario, rol);
END //

CREATE PROCEDURE sp_EnviarMensaje (
    IN id_emisor INT,
    IN id_receptor INT,
    IN id_chat INT,
    IN contenido VARBINARY(4096),
    IN estado_envio VARCHAR(20)
)
BEGIN
    INSERT INTO Mensaje (id_emisor, id_receptor, id_chat, contenido, estado_envio)
    VALUES (id_emisor, id_receptor, id_chat, contenido, estado_envio);
END //

CREATE PROCEDURE sp_CambiarEstadoMensaje (
    IN id_mensaje INT,
    IN nuevo_estado VARCHAR(20)
)
BEGIN
    UPDATE Mensaje
    SET estado_envio = nuevo_estado
    WHERE id_mensaje = id_mensaje;
END //

DELIMITER ;
