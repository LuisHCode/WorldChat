CREATE OR ALTER PROCEDURE [dbo].[sp_AgregarParticipante]
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
        SELECT 1 AS exito
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000);
        SET @ErrorMessage = ERROR_MESSAGE();

        THROW 50000, @ErrorMessage, 1;
    END CATCH
END;

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_CambiarEstadoMensaje]
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

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_CrearChat]
    @nombre_chat VARCHAR(100),
    @id_creador INT
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_creador)
            THROW 50004, 'El usuario creador no existe.', 1;

        INSERT INTO Chat (nombre_chat, id_creador)
        VALUES (@nombre_chat, @id_creador);

        DECLARE @id_chat INT = SCOPE_IDENTITY();

        INSERT INTO Participante (id_chat, id_usuario, rol)
        VALUES (@id_chat, @id_creador, 'Administrador');
        SELECT 1 AS exito;
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000);
        SET @ErrorMessage = ERROR_MESSAGE();

        THROW 50000, @ErrorMessage, 1;
    END CATCH
END;

GO

CREATE OR ALTER   PROCEDURE [dbo].[sp_CrearUsuario]
    @nombre_usuario VARCHAR(50),
    @nombre_completo VARCHAR(100),
    @telefono VARCHAR(20),
    @correo VARCHAR(100),
    @contrasenna VARBINARY(MAX), 
    @foto_perfil VARCHAR(255) = NULL,
    @estado VARCHAR(20) = 'Activo'
AS
BEGIN
    BEGIN TRY
        IF EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = @nombre_usuario)
            THROW 50001, 'El nombre de usuario ya está en uso.', 1;

        IF EXISTS (SELECT 1 FROM Usuario WHERE correo = @correo)
            THROW 50002, 'El correo ya está registrado.', 1;

        IF EXISTS (SELECT 1 FROM Usuario WHERE telefono = @telefono)
            THROW 50003, 'El número de teléfono ya está registrado.', 1;

        INSERT INTO Usuario (nombre_usuario, nombre_completo, telefono, correo, contrasenna, foto_perfil, estado)
        VALUES (@nombre_usuario, @nombre_completo, @telefono, @correo, @contrasenna, @foto_perfil, @estado);
    END TRY
    BEGIN CATCH
        THROW; -- para que FastAPI lo reciba
    END CATCH
END;

GO

CREATE OR ALTER   PROCEDURE [dbo].[sp_EliminarParticipante]
    @id_chat INT,
    @id_usuario INT,
    @id_admin INT
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50005, 'El chat no existe.', 1

        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario)
            THROW 50006, 'El usuario no existe.', 1

        IF NOT EXISTS (
            SELECT 1 FROM Participante 
            WHERE id_chat = @id_chat AND id_usuario = @id_usuario
        )
            THROW 50007, 'El usuario no es participante del chat.', 1

        IF NOT EXISTS (SELECT 1 FROM Participante WHERE id_chat = @id_chat AND id_usuario = @id_admin AND rol = 'Administrador')
            THROW 50008, 'El Usuario no es administrador.', 1

        DELETE FROM Participante
        WHERE id_usuario = @id_usuario AND id_chat = @id_chat

        SELECT 1 AS exito
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000);
        SET @ErrorMessage = ERROR_MESSAGE();

        THROW 50000, @ErrorMessage, 1;
    END CATCH
END;

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_EnviarMensaje] -- tenia clave
    @id_emisor INT,
    @id_chat INT,
    @contenido_texto VARBINARY(MAX),
    @estado_envio VARCHAR(20) = 'Enviado'
AS
BEGIN
    SET NOCOUNT ON;  -- 🔁 Previene mensajes de conteo (importantísimo para que FastAPI lo entienda bien)

    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_emisor)
            THROW 50008, 'El emisor no existe.', 1;

        IF @id_chat IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50011, 'El chat no existe.', 1;

        INSERT INTO Mensaje (id_emisor, id_chat, contenido, estado_envio)
        VALUES (@id_emisor, @id_chat, @contenido_texto, @estado_envio);

        -- ✅ Este SELECT debe venir después del insert y sin nada más abajo
        SELECT 1 AS exito;
    END TRY
BEGIN CATCH
    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    DECLARE @ErrorNumber INT = ERROR_NUMBER();
    SELECT 0 AS exito, @ErrorMessage AS error, @ErrorNumber AS codigo_error;
END CATCH

END;

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_EnviarMensajePrivado]
    @id_emisor INT,
    @id_receptor INT,
    @contenido VARBINARY(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Validar existencia del emisor
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_emisor)
            THROW 50001, 'El usuario emisor no existe.', 1;

        -- Validar existencia del receptor
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_receptor)
            THROW 50002, 'El usuario receptor no existe.', 1;

        -- Validar contenido
        IF @contenido IS NULL OR LTRIM(RTRIM(@contenido)) = ''
            THROW 50003, 'El contenido del mensaje no puede estar vacío.', 1;

        -- Insertar mensaje
        INSERT INTO Mensaje (id_emisor, id_receptor, contenido, estado_envio)
        VALUES (@id_emisor, @id_receptor, @contenido, 'Enviado');

        -- Devolver confirmación
        SELECT 1 AS exito;
    END TRY
    BEGIN CATCH
        -- Devolver error como result set para FastAPI
        DECLARE @ErrorMessage NVARCHAR(4000);
        SELECT @ErrorMessage = ERROR_MESSAGE();

        -- Puedes lanzar THROW si quieres que FastAPI lo capture como excepción
        THROW 50000, @ErrorMessage, 1;

        -- O alternativamente:
        -- SELECT 0 AS exito, @ErrorMessage AS error;
    END CATCH
END;

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_LeerMensajesChat] -- tenia clave
    @id_chat INT
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Chat WHERE id_chat = @id_chat)
            THROW 50020, 'El chat no existe.', 1

        SELECT 
            m.id_mensaje,
            u.nombre_usuario AS emisor,
            m.contenido,
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

CREATE OR ALTER   PROCEDURE [dbo].[sp_ModificarUsuario]
    @id_usuario INT,
    @nombre_usuario VARCHAR(50) = NULL,
    @nombre_completo VARCHAR(100) = NULL,
    @telefono VARCHAR(20) = NULL,
    @correo VARCHAR(100) = NULL,
    @contrasenna VARBINARY(MAX) = NULL,  -- Ahora acepta cifrado
    @foto_perfil VARCHAR(255) = NULL,
    @estado VARCHAR(20) = NULL
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario)
            THROW 50004, 'Usuario no encontrado.', 1;

        IF @nombre_usuario IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE nombre_usuario = @nombre_usuario AND id_usuario <> @id_usuario)
            THROW 50001, 'El nombre de usuario ya está en uso.', 1;

        IF @correo IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE correo = @correo AND id_usuario <> @id_usuario)
            THROW 50002, 'El correo ya está registrado.', 1;

        IF @telefono IS NOT NULL AND EXISTS (SELECT 1 FROM Usuario WHERE telefono = @telefono AND id_usuario <> @id_usuario)
            THROW 50003, 'El número de teléfono ya está registrado.', 1;

        UPDATE Usuario SET
            nombre_usuario = COALESCE(@nombre_usuario, nombre_usuario),
            nombre_completo = COALESCE(@nombre_completo, nombre_completo),
            telefono = COALESCE(@telefono, telefono),
            correo = COALESCE(@correo, correo),
            contrasenna = CASE WHEN @contrasenna IS NOT NULL THEN @contrasenna ELSE contrasenna END,
            foto_perfil = COALESCE(@foto_perfil, foto_perfil),
            estado = COALESCE(@estado, estado)
        WHERE id_usuario = @id_usuario;
    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END;

GO

CREATE OR ALTER PROCEDURE [dbo].[sp_ObtenerMensajesPrivados] --tenia clave
    @id_usuario1 INT,
    @id_usuario2 INT
AS
BEGIN
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario1)
            THROW 50022, 'El usuario 1 no existe.', 1;
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario2)
            THROW 50023, 'El usuario 2 no existe.', 1;

        SELECT 
            m.id_mensaje,
            m.id_emisor,
            u.nombre_usuario AS emisor,
            m.contenido,
            m.fecha_envio,
            m.estado_envio
        FROM Mensaje m
        INNER JOIN Usuario u ON m.id_emisor = u.id_usuario
        WHERE ((m.id_emisor = @id_usuario1 AND m.id_receptor = @id_usuario2)
           OR (m.id_emisor = @id_usuario2 AND m.id_receptor = @id_usuario1))
           AND m.id_chat IS NULL
        ORDER BY m.fecha_envio ASC
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;


GO

CREATE OR ALTER PROCEDURE sp_traerChatsPrivado
    @id_usuario INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Validar existencia del emisor
        IF NOT EXISTS (SELECT 1 FROM Usuario WHERE id_usuario = @id_usuario)
            THROW 50001, 'El usuario no existe.', 1;

        SELECT DISTINCT
            u.id_usuario, 
            u.nombre_usuario, 
            u.nombre_completo,
            u.telefono, 
            u.correo,
            u.foto_perfil,
            -- Obtener el último mensaje entre el usuario y este contacto
            (SELECT TOP 1 m.contenido 
             FROM Mensaje m
             WHERE (m.id_emisor = u.id_usuario AND m.id_receptor = @id_usuario)
                OR (m.id_emisor = @id_usuario AND m.id_receptor = u.id_usuario)
             ORDER BY m.fecha_envio DESC) AS ultimo_mensaje,
             (SELECT TOP 1 m.id_mensaje 
             FROM Mensaje m
             WHERE (m.id_emisor = u.id_usuario AND m.id_receptor = @id_usuario)
                OR (m.id_emisor = @id_usuario AND m.id_receptor = u.id_usuario)
             ORDER BY m.fecha_envio DESC) AS id_mensaje
        FROM 
            Usuario u
        JOIN
            Mensaje m 
                ON u.id_usuario = m.id_receptor OR u.id_usuario = m.id_emisor
        WHERE
            (m.id_emisor = @id_usuario OR m.id_receptor = @id_usuario)
            AND u.id_usuario != @id_usuario
        ORDER BY
            id_mensaje DESC        
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;

GO

CREATE OR ALTER PROCEDURE sp_buscarUsuarios
    @argumento NVARCHAR(100),
    @id_usuario INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        SELECT DISTINCT
            u.id_usuario, 
            u.nombre_usuario, 
            u.nombre_completo,
            u.telefono, 
            u.correo,
            u.foto_perfil,
            -- Obtener el último mensaje entre el usuario y este contacto
            -- Si no hay mensajes, devolver NULL
            ISNULL((
                SELECT TOP 1 m.contenido 
                FROM Mensaje m
                WHERE (m.id_emisor = u.id_usuario AND m.id_receptor = @id_usuario)
                    OR (m.id_emisor = @id_usuario AND m.id_receptor = u.id_usuario)
                ORDER BY m.fecha_envio DESC
            ), NULL) AS ultimo_mensaje
        FROM 
            Usuario u
        LEFT JOIN
            Mensaje m 
                ON (u.id_usuario = m.id_receptor OR u.id_usuario = m.id_emisor)
                AND (m.id_emisor = @id_usuario OR m.id_receptor = @id_usuario)
        WHERE
            u.id_usuario != @id_usuario
            AND (
                u.nombre_usuario LIKE '%' + @argumento + '%'   -- Buscar por nombre de usuario
                OR u.correo LIKE '%' + @argumento + '%'         -- Buscar por correo
            );
    END TRY
    BEGIN CATCH
        PRINT ERROR_MESSAGE()
    END CATCH
END;


select * from Mensaje