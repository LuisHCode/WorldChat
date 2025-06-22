def crear_estructura_sqlserver(cursor):
    import logica.crear_estructura_sqlserver as m

    conn = obtener_conexion_sqlserver()
    if conn:
        cursor = conn.cursor()
        m.crear_estructura_sqlserver(cursor)
        conn.commit()
        cursor.close()
        conn.close()


def crear_estructura_mysql(cursor):
    import logica.crear_estructura_mysql as m

    conn = obtener_conexion_mysql()
    if conn:
        cursor = conn.cursor()
        m.crear_estructura_si_no_existe_mysql(cursor)
        conn.commit()
        cursor.close()
        conn.close()


def restaurar_datos_sqlserver():
    import logica.restauracion_a_sqlserver


def restaurar_datos_mysql():
    import logica.restauracion_a_mysql


def exportar_datos_sqlserver():
    import logica.transformacion_sqlserver


def exportar_datos_mysql():
    import logica.transformacion_mysql


def verificar_conexion_sqlserver():
    import conexion.conexion_sqlserver as s
    conn = s.obtener_conexion_sqlserver()
    if conn:
        print("✅ Conexión a SQL Server verificada correctamente.")
        conn.close()
    else:
        print("❌ No se pudo conectar a SQL Server.")


def verificar_conexion_mysql():
    import conexion.conexion_mysql as m
    conn = m.obtener_conexion_mysql()
    if conn:
        print("✅ Conexión a MySQL verificada correctamente.")
        conn.close()
    else:
        print("❌ No se pudo conectar a MySQL.")


def ver_datos_desencriptados():
    from logica.ver_datos_desencriptados import main as ver_datos_main

    ver_datos_main()


def prueba():
    print("debe imprimir")


def ejecutar_opcion(opcion):
    if opcion == "1":
        crear_estructura_sqlserver()
    elif opcion == "2":
        crear_estructura_mysql()
    elif opcion == "3":
        restaurar_datos_sqlserver()
    elif opcion == "4":
        restaurar_datos_mysql()
    elif opcion == "5":
        exportar_datos_sqlserver()
    elif opcion == "6":
        exportar_datos_mysql()()
    elif opcion == "7": 
        verificar_conexion_sqlserver()
    elif opcion == "8":
        verificar_conexion_mysql()
    elif opcion == "9":
        ver_datos_desencriptados()
    elif opcion == "0":
        print("Saliendo...")
        exit()
    else:
        print("Opción no válida")
