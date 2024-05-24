import mysql.connector
import os
from dotenv import load_dotenv
from flask import flash
import requests
import logging



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
def insertar_usuario(id_targeta, nombre, apellido, estado):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO usuarios (ID_Targeta, Nombre, Apellido, Estado) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id_targeta, nombre, apellido, estado))
        conn.commit()
        return cursor.lastrowid  # Retorna l'ID de l'usuari inserit
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error al insertar usuario: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




def insertar_clave(id_usuario_key, clave_id, clave):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO claves_targeta (ID_usuari_Key, ID, Clave) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_usuario_key, clave_id, clave))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error al insertar clave: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




def insertar_acceso(id_usuario, puerta_1, puerta_2, puerta_3, puerta_4, puerta_5):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO accesos (ID_Usuario_Acceso, Puerta_1, Puerta_2, Puerta_3, Puerta_4, Puerta_5) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (id_usuario, puerta_1, puerta_2, puerta_3, puerta_4, puerta_5))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error al insertar acceso: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()





# Directorio temporal para guardar los archivos ZIP
DIRECTORIO_TEMPORAL = '/home/ubuntu/web/temporal'

# Directorio para guardar los registros
DIRECTORIO_LOGS = '/home/ubuntu/web/logs'

# Configuración del registro
logging.basicConfig(filename=os.path.join(DIRECTORIO_LOGS, 'subir_archivos.log'), level=logging.DEBUG)

def subir_archivo_zip(archivo_zip):
    try:
        ruta_archivo_zip = os.path.join(DIRECTORIO_TEMPORAL, archivo_zip.filename)
        archivo_zip.save(ruta_archivo_zip)
        logging.info(f"Archivo ZIP guardado exitosamente en {ruta_archivo_zip}")
        
        with open(ruta_archivo_zip, 'rb') as f:
            files = {'file': (archivo_zip.filename, f)}
            response = requests.post('https://beta-bbdd.duckdns.org/upload', files=files)
            if response.status_code == 200:
                logging.info("Archivo ZIP enviado exitosamente")
                os.remove(ruta_archivo_zip)
                logging.info("Archivo ZIP eliminado exitosamente")
                return True
            else:
                logging.error(f"Fallo al enviar archivo ZIP: {response.status_code}")
                return False
    except Exception as e:
        logging.error(f"Error al enviar archivo ZIP: {e}")
        raise

