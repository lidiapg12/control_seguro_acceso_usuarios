import mysql.connector
from dotenv import load_dotenv
import os

# Cargar configuración de la base de datos desde variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), 'entorno.env'))
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

def actualizar_estado_tarjeta(id_usuario, estado):
    conn = mysql.connector.connect(**db_config)  # Asegúrate de definir db_config con tus credenciales de conexión
    cursor = conn.cursor()
    try:
        # Verificar si el ID de usuario existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE ID_Usuario = %s", (id_usuario,))
        (count,) = cursor.fetchone()
        if count == 0:
            return "ID de usuario no existe.", False

        # Si el ID existe, actualizar el estado
        cursor.execute("UPDATE usuarios SET Estado = %s WHERE ID_Usuario = %s", (estado, id_usuario))
        conn.commit()
        if cursor.rowcount == 0:
            return "No se realizó ningún cambio.", False
        return "Estado de la tarjeta actualizado correctamente.", True
    except mysql.connector.Error as error:
        return f"Error al actualizar el estado de la tarjeta: {error}", False
    finally:
        cursor.close()
        conn.close()

def actualizar_clave_db(id_usuario, nueva_clave):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # Primero, verificar si el usuario existe
        cursor.execute("SELECT COUNT(*) FROM claves_targeta WHERE ID_usuari_Key = %s", (id_usuario,))
        (count,) = cursor.fetchone()
        if count == 0:
            return "ID de usuario no existe.", False
        
        # Si el usuario existe, actualizar la clave
        cursor.execute("UPDATE claves_targeta SET Clave = %s WHERE ID_usuari_Key = %s", (nueva_clave, id_usuario))
        conn.commit()
        if cursor.rowcount == 0:
            return "No se realizó ningún cambio.", False
        return "Clave actualizada correctamente.", True
    except mysql.connector.Error as error:
        return f"Error al actualizar la clave: {error}", False
    finally:
        cursor.close()
        conn.close()


def actualizar_accesos(id_usuario_acceso, puerta_1, puerta_2, puerta_3, puerta_4, puerta_5):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE accesos SET 
            Puerta_1 = %s, Puerta_2 = %s, Puerta_3 = %s, Puerta_4 = %s, Puerta_5 = %s 
            WHERE ID_Usuario_Acceso = %s
        """, (puerta_1, puerta_2, puerta_3, puerta_4, puerta_5, id_usuario_acceso))
        conn.commit()
        return "Accesos actualizados correctamente.", True
    except mysql.connector.Error as error:
        return f"Error al actualizar los accesos: {error}", False
    finally:
        cursor.close()
        conn.close()

