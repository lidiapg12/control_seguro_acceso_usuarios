import re  # Importa el mòdul re per a expressions regulars
import os  # Importa el mòdul os per a funcions del sistema operatiu
import hashlib  # Importa el mòdul hashlib per a funcions de hash
from flask import Flask, request, make_response  # Importa classes necessàries de Flask
import mysql.connector  # Importa el connector MySQL per a la connexió amb la base de dades
from dotenv import load_dotenv  # Importa la funció load_dotenv per a carregar variables d'entorn

# Configuració del directori i càrrega de variables d'entorn
DIRECTORIO = "/home/ubuntu/myproject"
env_path = '/home/ubuntu/secure_card/bbdd_claves.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)  # Inicialitza l'aplicació Flask

# Variables de connexió a la base de dades
DATABASE = os.getenv('DB_DATABASE')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
FERNET_KEY = os.getenv('FERNET_KEY')

# Funció per obtenir una connexió a la base de dades
def get_db_connection():
    try:
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}", file=sys.stderr)
        return None

# Funció per enregistrar registres de log a la base de dades
def registrar_log(id_targeta, puerta, acceso):
    db = get_db_connection()
    if db is None:
        print("Failed to connect to database for logging.", file=sys.stderr)
        return

    cursor = db.cursor()
    try:
        query = "INSERT INTO logs (ID_Targeta_Log, Puerta, Acceso) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_targeta, puerta, int(acceso)))
        db.commit()
    except Exception as e:
        print(f"Error al registrar log: {e}")
    finally:
        cursor.close()
        db.close()

# Ruta per a processar les dades rebudes
@app.route('/procesar_datos', methods=['POST'])
def procesar_datos():
    numero_rfid = request.form.get('numero_rfid', '')
    puerta = request.form.get('puerta', '')

    if not re.match("^\d+$", numero_rfid):  # Comprova si el número RFID té un format vàlid
        registrar_log(numero_rfid, puerta, 0)  # Registra un log d'accés denegat
        return make_response("false\n", 200, {'Content-Type': 'text/plain'})

    db = get_db_connection()
    if db is None:
        return make_response("Database connection failed", 500)

    cursor = db.cursor()
    try:
        cursor.execute("SELECT Estado, ID_Usuario FROM usuarios WHERE ID_Targeta = %s", (numero_rfid,))
        resultado = cursor.fetchone()

        if resultado is None or resultado[0] != 1:  # Comprova si la targeta està activa
            registrar_log(numero_rfid, puerta, 0)  # Registra un log d'accés denegat
            return make_response("false\n", 200, {'Content-Type': 'text/plain'})

        estado, id_usuario = resultado
        acceso_concedido = True if estado == 1 else False

        # Comprova si l'usuari té accés a la porta
        columna_puerta = f'Puerta_{puerta}'
        cursor.execute(f"SELECT {columna_puerta} FROM accesos WHERE ID_Usuario_Acceso = %s", (id_usuario,))
        acceso_result = cursor.fetchone()

        if acceso_result is None or acceso_result[0] != 1:  # Comprova si s'ha concedit l'accés
            registrar_log(numero_rfid, puerta, 0)  # Registra un log d'accés denegat
            return make_response("false\n", 200, {'Content-Type': 'text/plain'})

        if acceso_concedido:  # Si s'ha concedit l'accés
            cursor.execute("SELECT Nombre FROM usuarios WHERE ID_Usuario = %s", (id_usuario,))
            nombre_usuario = cursor.fetchone()[0].strip().lower()
            hash_nombre = hashlib.sha256(nombre_usuario.encode()).hexdigest()  # Genera un hash del nom de l'usuari
            ruta_archivo_hash = os.path.join(DIRECTORIO, "hash.txt")
            with open(ruta_archivo_hash, "w") as archivo:
                archivo.write(hash_nombre)

            ruta_archivo_log = os.path.join(DIRECTORIO, "name_log.txt")
            with open(ruta_archivo_log, "w") as archivo_log:
                archivo_log.write(f"{numero_rfid}\n")  # Guarda el número RFID a un fitxer de log
    except Exception as e:
        print(f"Error al procesar datos: {e}")
        if resultado:
            registrar_log(numero_rfid, puerta, 0)  # Registra un log d'accés denegat
        return make_response("false\n", 500)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

    response_text = "true\n" if acceso_concedido else "false\n"
    return make_response(response_text, 200, {'Content-Type': 'text/plain'})

# Inicia l'aplicació Flask per escoltar les sol·licituds HTTP
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
