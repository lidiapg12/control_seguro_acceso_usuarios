import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Cargar variables de entorno desde el archivo entorno.env
load_dotenv('/home/ubuntu/web/entorno.env')

# Obtener los valores de las variables de entorno
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")

# Crear la configuración de la base de datos
db_config = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_database
}

def obtener_conexion():
    return mysql.connector.connect(**db_config)  # Asegúrate de tener tus credenciales aquí

def contar_usuarios():
    conn = obtener_conexion()  # Obtener la conexión a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar consultas SQL
    query = "SELECT COUNT(*) FROM usuarios"  # Consulta para contar los usuarios
    cursor.execute(query)  # Ejecutar la consulta
    count = cursor.fetchone()[0]  # Obtener el resultado de la consulta
    cursor.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión a la base de datos
    return count  # Devolver el número de usuarios



def obtener_accesos_por_usuario():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Calcular la fecha y hora hace 24 horas
    fecha_hora_24h_atras = datetime.now() - timedelta(hours=24)

    query = """
    SELECT 
        ID_Tarjeta,
        Nombre_Usuario,
        Apellido_Usuario,
        COUNT(CASE WHEN Acceso = 1 THEN 1 END) AS Accesos_Concedidos,
        COUNT(CASE WHEN Acceso = 0 THEN 1 END) AS Accesos_Denegados
    FROM 
        vista_logs
    WHERE 
        Fecha_Hora >= %s
    GROUP BY 
        ID_Tarjeta, Nombre_Usuario, Apellido_Usuario
    ORDER BY 
        Nombre_Usuario, Apellido_Usuario
    """

    cursor.execute(query, (fecha_hora_24h_atras,))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados


def obtener_accesos_por_puerta():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Calcular la fecha y hora hace 24 horas
    fecha_hora_24h_atras = datetime.now() - timedelta(hours=24)

    query = """
    SELECT 
        Puerta,
        SUM(CASE WHEN Acceso = 1 THEN 1 ELSE 0 END) AS Accesos_Concedidos,
        SUM(CASE WHEN Acceso = 0 THEN 1 ELSE 0 END) AS Accesos_Denegados
    FROM 
        vista_logs
    WHERE 
        Fecha_Hora >= %s
    GROUP BY 
        Puerta
    ORDER BY 
        Puerta
    """

    cursor.execute(query, (fecha_hora_24h_atras,))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados

