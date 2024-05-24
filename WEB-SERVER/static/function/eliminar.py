import os
import mysql.connector
from dotenv import load_dotenv
import shutil

# Cargar variables de entorno desde el archivo
load_dotenv('entorno.env')

def eliminar_usuario_db(user_id):
    try:
        # Usar variables de entorno en la conexión a la base de datos
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        cursor = conn.cursor()

        # Obtener el nombre de usuario asociado al ID
        cursor.execute('SELECT Nombre FROM usuarios WHERE ID_Usuario = %s', (user_id,))
        result = cursor.fetchone()
        if result:
            username = result[0]  # No es necesario convertir a minúsculas
            # Construir la ruta del directorio a eliminar
            directory_path = f"/home/ubuntu/bbddphotos/bbdd-directory/{username}"
            
            # Verificar si el directorio existe antes de intentar eliminarlo
            if os.path.exists(directory_path):
                # Eliminar el directorio y su contenido
                shutil.rmtree(directory_path)

        # Eliminar registros relacionados en la base de datos
        cursor.execute('DELETE FROM claves_targeta WHERE ID_usuari_Key = %s', (user_id,))
        cursor.execute('DELETE FROM accesos WHERE ID_Usuario_Acceso = %s', (user_id,))
        cursor.execute('DELETE FROM usuarios WHERE ID_Usuario = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Error al eliminar usuario:", e)
        return False
