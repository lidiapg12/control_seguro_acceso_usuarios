# /home/ubuntu/web/static/function/usuarios.py
import mysql.connector

def obtener_usuarios(db_config):
    """Consulta la base de datos y devuelve todos los usuarios."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return usuarios
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []


# BBDD TARGETA

def obtener_tarjetas(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM claves_targeta")
        tarjetas = cursor.fetchall()
        cursor.close()
        conn.close()
        return tarjetas
    except Exception as e:
        print(f"Error al obtener tarjetas: {e}")
        return []

def obtener_logs(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vista_logs")
        logs = cursor.fetchall()  # Corregido: asigna los resultados a 'logs'
        cursor.close()
        conn.close()
        return logs  # Devuelve 'logs' en lugar de 'targetas'
    except Exception as e:
        print(f"Error al obtener logs: {e}")
        return []


def obtener_accesos(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM accesos")
        accesos = cursor.fetchall()  # Corregido: asigna los resultados a 'logs'
        cursor.close()
        conn.close()
        return accesos  
    except Exception as e:
        print(f"Error al obtener accesos: {e}")
        return []

