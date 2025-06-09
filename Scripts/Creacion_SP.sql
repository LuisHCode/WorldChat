CREATE PROCEDURE sp_CrearUsuario
    @nombre_usuario VARCHAR(50),
    @nombre_completo VARCHAR(100),
    @telefono VARCHAR(20),
    @correo VARCHAR(100),
    @contrasenna VARCHAR(100), 
    @foto_perfil VARCHAR(255) = NULL,
    @estado VARCHAR(20) = 'Activo'
AS
BEGIN
    BEGIN TRY
        IF EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = @nombre_usuario)
            THROW 50001, 'El nombre de usuario ya est� en uso.', 1;

        IF EXISTS (SELECT 1 FROM Usuario WHERE correo = @correo)
            THROW 50002, 'El correo ya est� registrado.', 1;

        IF EXISTS (SELECT 1 FROM Usuario WHERE telefono = @telefono)
            THROW 50003, 'El n�mero de tel�fono ya est� registrado.', 1;

        -- Variable para el hash de la contrase�a
        DECLARE @contrasenna_hash VARBINARY(MAX);

        -- Hashear la contrase�a usando SHA2_256
        SET @contrasenna_hash = HASHBYTES('SHA2_256', @contrasenna);

        -- Insertar el usuario con el hash
        INSERT INTO Usuario (nombre_usuario, nombre_completo, telefono, correo, contrasenna, foto_perfil, estado)
        VALUES (@nombre_usuario, @nombre_completo, @telefono, @correo, @contrasenna_hash, @foto_perfil, @estado);
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE();
    END CATCH
END;

GO

CREATE PROCEDURE sp_ModificarUsuario
    @id_usuario INT,
    @nombre_usuario VARCHAR(50) = NULL,
    @nombre_completo VARCHAR(100) = NULL,
    @telefono VARCHAR(20) = NULL,
    @correo VARCHAR(100) = NULL,
    @contrasenna VARCHAR(100) = NULL,  -- texto plano, opcional
    @foto_perfil VARCHAR(255) = NULL,
    @estado VARCHAR(20) = NULL
AS
BEGIN
    BEGIN TRY
        -- Validar que el usuario exista
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario)
            THROW 50004, 'Usuario no encontrado.', 1;

        -- Validar unicidad si cambian campos �nicos
        IF @nombre_usuario IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = @nombre_usuario AND id_usuario <> @id_usuario)
            THROW 50001, 'El nombre de usuario ya est� en uso.', 1;

        IF @correo IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE correo = @correo AND id_usuario <> @id_usuario)
            THROW 50002, 'El correo ya est� registrado.', 1;

        IF @telefono IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE telefono = @telefono AND id_usuario <> @id_usuario)
            THROW 50003, 'El n�mero de tel�fono ya est� registrado.', 1;

        -- Variable para hash contrase�a si se actualiza
        DECLARE @contrasenna_hash VARBINARY(MAX) = NULL;
        IF @contrasenna IS NOT NULL
            SET @contrasenna_hash = HASHBYTES('SHA2_256', @contrasenna);

        -- Actualizar solo los campos que no sean NULL (excepto id)
        UPDATE Usuario SET
            nombre_usuario = COALESCE(@nombre_usuario, nombre_usuario),
            nombre_completo = COALESCE(@nombre_completo, nombre_completo),
            telefono = COALESCE(@telefono, telefono),
            correo = COALESCE(@correo, correo),
            contrasenna = CASE WHEN @contrasenna IS NOT NULL THEN @contrasenna_hash ELSE contrasenna END,
            foto_perfil = COALESCE(@foto_perfil, foto_perfil),
            estado = COALESCE(@estado, estado)
        WHERE id_usuario = @id_usuario;
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE();
    END CATCH
END;


GO

CREATE PROCEDURE sp_CrearChat
    @nombre_chat VARCHAR(100),
    @id_creador INT
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_creador)
            THROW 50004, 'El usuario creador no existe.', 1

        INSERT INTO Chat (nombre_chat, id_creador)
        VALUES (@nombre_chat, @id_creador)

        DECLARE @id_chat INT = SCOPE_IDENTITY()

        INSERT INTO Participante (id_chat, id_usuario, rol)
        VALUES (@id_chat, @id_creador, 'Administrador')
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;

GO


CREATE PROCEDURE sp_AgregarParticipante
    @id_chat INT,
    @id_usuario INT,
    @rol VARCHAR(20) = 'Miembro'
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50005, 'El chat no existe.', 1

        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario)
            THROW 50006, 'El usuario no existe.', 1

        IF EXISTS (
            SELECT 1 FROM Participante 
            WHERE id_chat = @id_chat AND id_usuario = @id_usuario
        )
            THROW 50007, 'El usuario ya es participante del chat.', 1

        INSERT INTO Participante (id_chat, id_usuario, rol)
        VALUES (@id_chat, @id_usuario, @rol)
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;

GO
CREATE OR ALTER PROCEDURE sp_EnviarMensajePrivado
    @id_emisor INT,
    @id_receptor INT,
    @contenido VARCHAR(MAX)
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_emisor)
            THROW 50010, 'Emisor no encontrado.', 1;

        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_receptor)
            THROW 50011, 'Receptor no encontrado.', 1;

        OPEN SYMMETRIC KEY ClaveSimetrica
            DECRYPTION BY CERTIFICATE MiCertificadoConClave;

        DECLARE @contenido_encriptado VARBINARY(MAX) = 
            EncryptByKey(Key_GUID('ClaveSimetrica'), CONVERT(VARBINARY(MAX), @contenido));

        INSERT INTO Mensaje (id_emisor, id_receptor, contenido, fecha_envio, estado_envio)
        VALUES (@id_emisor, @id_receptor, @contenido_encriptado, GETDATE(), 'Enviado');

        CLOSE SYMMETRIC KEY ClaveSimetrica;

        SELECT 1 AS exito;
    END TRY
    BEGIN CATCH
        SELECT 0 AS exito;
    END CATCH
END;


GO


CREATE OR ALTER PROCEDURE sp_EnviarMensaje
    @id_emisor INT,
    @id_chat INT,
    @contenido NVARCHAR(MAX) -- Se recibe en texto
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_emisor)
            THROW 50008, 'El emisor no existe.', 1

        IF @id_chat IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50011, 'El chat no existe.', 1

        OPEN SYMMETRIC KEY ClaveSimetrica
            DECRYPTION BY CERTIFICATE MiCertificadoConClave;

        -- Cifrar el contenido
         DECLARE @contenido_encriptado VARBINARY(MAX) = 
            EncryptByKey(Key_GUID('ClaveSimetrica'), CONVERT(VARBINARY(MAX), @contenido));

        INSERT INTO Mensaje (id_emisor, id_chat, contenido, estado_envio)
        VALUES (@id_emisor,@id_chat, @contenido_encriptado, 'Enviado')

        CLOSE SYMMETRIC KEY ClaveSimetrica;
        SELECT 1 AS exito;
    END TRY
    BEGIN CATCH
        SELECT 0 AS exito;
    END CATCH
END;

GO


CREATE PROCEDURE sp_LeerMensajesChat
    @id_chat INT,
    @clave NVARCHAR(100) -- Clave para descifrar
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50020, 'El chat no existe.', 1

        SELECT 
            m.id_mensaje,
            u.nombre_usuario AS emisor,
            CONVERT(NVARCHAR(MAX), DecryptByPassPhrase(@clave, m.contenido)) AS contenido_descifrado,
            m.fecha_envio,
            m.estado_envio
        FROM Mensaje m
        INNER JOIN Usuario u ON m.id_emisor = u.id_usuario
        WHERE m.id_chat = @id_chat
        ORDER BY m.fecha_envio ASC
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;

GO


CREATE OR ALTER PROCEDURE sp_ObtenerMensajesPrivados
    @id_usuario1 INT,
    @id_usuario2 INT
AS
BEGIN
    BEGIN TRY
        OPEN SYMMETRIC KEY ClaveSimetrica
            DECRYPTION BY CERTIFICATE MiCertificadoConClave;

        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario1)
            THROW 50022, 'El usuario 1 no existe.', 1;

        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario2)
            THROW 50023, 'El usuario 2 no existe.', 1;

        SELECT 
            m.id_mensaje,
            u.nombre_usuario AS emisor,
            CONVERT(VARCHAR(MAX), DecryptByKey(m.contenido)) AS contenido,
            m.fecha_envio,
            m.estado_envio
        FROM Mensaje m
        INNER JOIN Usuario u ON m.id_emisor = u.id_usuario
        WHERE (m.id_emisor = @id_usuario1 AND m.id_receptor = @id_usuario2)
           OR (m.id_emisor = @id_usuario2 AND m.id_receptor = @id_usuario1)
        ORDER BY m.fecha_envio ASC;

        CLOSE SYMMETRIC KEY ClaveSimetrica;
    END TRY
    BEGIN CATCH
            CLOSE SYMMETRIC KEY ClaveSimetrica;
        THROW;
    END CATCH
END;
GO


GO


CREATE PROCEDURE sp_CambiarEstadoMensaje
    @id_mensaje INT,
    @nuevo_estado VARCHAR(20)
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Mensaje WHERE id_mensaje = @id_mensaje)
            THROW 50012, 'El mensaje no existe.', 1

        UPDATE Mensaje
        SET estado_envio = @nuevo_estado
        WHERE id_mensaje = @id_mensaje
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;
