# ProyectoWorldChat

## Descripción del Proyecto
ProyectoWorldChat es una aplicación de mensajería que permite la gestión de datos en bases de datos SQL Server y MySQL. La aplicación ofrece diversas funcionalidades, incluyendo la creación de estructuras de base de datos, restauración de datos desde archivos Excel, y exportación de datos a Excel.

## Estructura del Proyecto
El proyecto está organizado en varias carpetas y archivos, cada uno con una función específica:

- **main/**
  - `main.py`: Punto de entrada de la aplicación que muestra un menú para la interacción del usuario y ejecuta diversas opciones relacionadas con operaciones de base de datos y gestión de datos.
  - `app.py`: Maneja la lógica de enrutamiento de la aplicación, definiendo funciones para gestionar las operaciones, lo que permite una mejor organización y separación de preocupaciones.

- **conexion/**
  - `conexion_sqlserver.py`: Contiene funciones para establecer una conexión con una base de datos SQL Server.
  - `conexion_mysql.py`: Contiene funciones para establecer una conexión con una base de datos MySQL.

- **logica/**
  - `crear_estructura_sqlserver.py`: Contiene la lógica para crear la estructura de la base de datos en SQL Server.
  - `crear_estructura_mysql.py`: Contiene la lógica para crear la estructura de la base de datos en MySQL.
  - `restauracion_a_sqlserver.py`: Contiene la lógica para restaurar datos a SQL Server desde Excel.
  - `restauracion_a_mysql.py`: Contiene la lógica para restaurar datos a MySQL desde Excel.
  - `transformacion_sqlserver.py`: Contiene la lógica para exportar datos desde SQL Server a Excel.
  - `transformacion_mysql.py`: Contiene la lógica para exportar datos desde MySQL a Excel.
  - `ver_datos_desencriptados.py`: Contiene la lógica para ver datos desencriptados con fines de prueba.

## Instalación
1. Clona el repositorio en tu máquina local.
2. Asegúrate de tener instaladas las dependencias necesarias para conectarte a SQL Server y MySQL.
3. Configura las conexiones en los archivos correspondientes dentro de la carpeta `conexion/`.

## Uso
Ejecuta el archivo `main.py` para iniciar la aplicación. Sigue las instrucciones en pantalla para interactuar con las diferentes funcionalidades disponibles.

## Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia
Este proyecto está bajo la Licencia MIT.