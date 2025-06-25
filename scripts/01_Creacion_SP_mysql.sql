Use ProyectoBD;

-- Usuario
DROP PROCEDURE IF EXISTS sp_CrearUsuario;
DELIMITER $$
CREATE PROCEDURE sp_CrearUsuario(
    IN p_nombre_usuario VARCHAR(50),
    IN p_nombre_completo VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(100),
    IN p_contrasenna VARBINARY(255),
    IN p_foto_perfil VARCHAR(255),
    IN p_estado VARCHAR(20)
)
BEGIN
    IF EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = p_nombre_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya está en uso.';
    END IF;
    IF EXISTS (SELECT 1 FROM Usuario WHERE correo = p_correo) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya está registrado.';
    END IF;
    IF EXISTS (SELECT 1 FROM Usuario WHERE telefono = p_telefono) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El número de teléfono ya está registrado.';
    END IF;

    INSERT INTO Usuario (nombre_usuario, nombre_completo, telefono, correo, contrasenna, foto_perfil, estado)
    VALUES (p_nombre_usuario, p_nombre_completo, p_telefono, p_correo, p_contrasenna, p_foto_perfil, p_estado);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_ModificarUsuario;
DELIMITER $$
CREATE PROCEDURE sp_ModificarUsuario(
    IN p_id_usuario INT,
    IN p_nombre_usuario VARCHAR(50),
    IN p_nombre_completo VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(100),
    IN p_contrasenna VARBINARY(255),
    IN p_foto_perfil VARCHAR(255),
    IN p_estado VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado.';
    END IF;

    IF p_nombre_usuario IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = p_nombre_usuario AND id_usuario <> p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya está en uso.';
    END IF;
    IF p_correo IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE correo = p_correo AND id_usuario <> p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El correo ya está registrado.';
    END IF;
    IF p_telefono IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE telefono = p_telefono AND id_usuario <> p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El número de teléfono ya está registrado.';
    END IF;

    UPDATE Usuario SET
        nombre_usuario = COALESCE(p_nombre_usuario, nombre_usuario),
        nombre_completo = COALESCE(p_nombre_completo, nombre_completo),
        telefono = COALESCE(p_telefono, telefono),
        correo = COALESCE(p_correo, correo),
        contrasenna = CASE WHEN p_contrasenna IS NOT NULL THEN p_contrasenna ELSE contrasenna END,
        foto_perfil = COALESCE(p_foto_perfil, foto_perfil),
        estado = COALESCE(p_estado, estado)
    WHERE id_usuario = p_id_usuario;
END$$
DELIMITER ;

-- Chat
DROP PROCEDURE IF EXISTS sp_CrearChat;
DELIMITER $$
CREATE PROCEDURE sp_CrearChat(
    IN p_nombre_chat VARCHAR(100),
    IN p_id_creador INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_creador) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario creador no existe.';
    END IF;

    INSERT INTO Chat (nombre_chat, id_creador) VALUES (p_nombre_chat, p_id_creador);
    SET @id_chat = LAST_INSERT_ID();
    INSERT INTO Participante (id_chat, id_usuario, rol)
    VALUES (@id_chat, p_id_creador, 'Administrador');
END$$
DELIMITER ;

-- Participante
DROP PROCEDURE IF EXISTS sp_AgregarParticipante;
DELIMITER $$
CREATE PROCEDURE sp_AgregarParticipante(
    IN p_id_chat INT,
    IN p_id_usuario INT,
    IN p_rol VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = p_id_chat) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El chat no existe.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe.';
    END IF;
    IF EXISTS (SELECT 1 FROM Participante WHERE id_chat = p_id_chat AND id_usuario = p_id_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario ya es participante del chat.';
    END IF;

    INSERT INTO Participante (id_chat, id_usuario, rol)
    VALUES (p_id_chat, p_id_usuario, p_rol);
END$$
DELIMITER ;

-- Mensaje privado
DROP PROCEDURE IF EXISTS sp_EnviarMensajePrivado;
DELIMITER $$
CREATE PROCEDURE sp_EnviarMensajePrivado(
    IN p_id_emisor INT,
    IN p_id_receptor INT,
    IN p_contenido VARBINARY(255)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_emisor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Emisor no encontrado.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_receptor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receptor no encontrado.';
    END IF;

    INSERT INTO Mensaje (id_emisor, id_receptor, contenido, fecha_envio, estado_envio)
    VALUES (p_id_emisor, p_id_receptor, p_contenido, NOW(), 'Enviado');
END$$
DELIMITER ;

-- Mensaje general
DROP PROCEDURE IF EXISTS sp_EnviarMensaje;
DELIMITER $$
CREATE PROCEDURE sp_EnviarMensaje(
    IN p_id_emisor INT,
    IN p_id_receptor INT,
    IN p_id_chat INT,
    IN p_contenido VARBINARY(255),
    IN p_estado_envio VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_emisor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El emisor no existe.';
    END IF;
    IF p_id_receptor IS NULL AND p_id_chat IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Debe especificar un receptor o un chat.';
    END IF;
    IF p_id_receptor IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_receptor) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El receptor no existe.';
    END IF;
    IF p_id_chat IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = p_id_chat) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El chat no existe.';
    END IF;

    INSERT INTO Mensaje (id_emisor, id_receptor, id_chat, contenido, estado_envio)
    VALUES (p_id_emisor, p_id_receptor, p_id_chat, p_contenido, p_estado_envio);
END$$
DELIMITER ;

-- Leer mensajes chat
DROP PROCEDURE IF EXISTS sp_LeerMensajesChat;
DELIMITER $$
CREATE PROCEDURE sp_LeerMensajesChat(
    IN p_id_chat INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = p_id_chat) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El chat no existe.';
    END IF;

    SELECT m.id_mensaje, u.nombre_usuario AS emisor,
           m.contenido, m.fecha_envio, m.estado_envio
    FROM Mensaje m
    INNER JOIN Usuario u ON m.id_emisor = u.id_usuario
    WHERE m.id_chat = p_id_chat
    ORDER BY m.fecha_envio ASC;
END$$
DELIMITER ;

-- Leer mensajes privados
DROP PROCEDURE IF EXISTS sp_ObtenerMensajesPrivados;
DELIMITER $$
CREATE PROCEDURE sp_ObtenerMensajesPrivados(
    IN p_id_usuario1 INT,
    IN p_id_usuario2 INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_usuario1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario 1 no existe.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = p_id_usuario2) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario 2 no existe.';
    END IF;

    SELECT m.id_mensaje, u.nombre_usuario AS emisor,
           m.contenido, m.fecha_envio, m.estado_envio
    FROM Mensaje m
    INNER JOIN Usuario u ON m.id_emisor = u.id_usuario
    WHERE (m.id_emisor = p_id_usuario1 AND m.id_receptor = p_id_usuario2)
       OR (m.id_emisor = p_id_usuario2 AND m.id_receptor = p_id_usuario1)
    ORDER BY m.fecha_envio ASC;
END$$
DELIMITER ;

-- Cambiar estado
DROP PROCEDURE IF EXISTS sp_CambiarEstadoMensaje;
DELIMITER $$
CREATE PROCEDURE sp_CambiarEstadoMensaje(
    IN p_id_mensaje INT,
    IN p_nuevo_estado VARCHAR(20)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Mensaje WHERE id_mensaje = p_id_mensaje) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El mensaje no existe.';
    END IF;

    UPDATE Mensaje SET estado_envio = p_nuevo_estado
    WHERE id_mensaje = p_id_mensaje;
END$$
DELIMITER ;
