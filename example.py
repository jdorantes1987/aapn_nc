import mysql.connector

# Tu código no necesita las credenciales del archivo JSON,
# solo la información del usuario y la base de datos.
DB_USER = "jdorantes"
DB_NAME = "AAPN"

try:
    connection = mysql.connector.connect(
        user=DB_USER,
        # Si tu usuario de la base de datos tiene una contraseña, inclúyela aquí.
        # No confundir con las credenciales de la cuenta de servicio.
        password="**",
        host="127.0.0.1",
        port=3306,
        database=DB_NAME,
    )
    print("✅ Conexión a Cloud SQL exitosa a través del proxy.")

    # Ejemplo de operación: Obtener la versión de la base de datos
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT username,
                      AES_DECRYPT(password,'123') as Contrasena
               FROM users"""
        )
        db_row = cursor.fetchall()
        print(f"Datos de la tabla: {db_row}")

except mysql.connector.Error as err:
    print(f"❌ Error al conectar a la base de datos: {err}")
finally:
    if "connection" in locals() and connection.is_connected():
        connection.close()
        print("Conexión cerrada.")
