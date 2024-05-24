import re  # Importa el mòdul re per a expressions regulars
import os  # Importa el mòdul os per a funcions del sistema operatiu
import hashlib  # Importa el mòdul hashlib per a funcions de hash
from flask import Flask, request, make_response  # Importa classes necessàries de Flask
import mysql.connector  # Importa el connector MySQL per a la connexió amb la base de dades
from dotenv import load_dotenv  # Importa la funció load_dotenv per a carregar variables d'entorn

DIRECTORIO = "/home/ubuntu/myproject"  # Defineix el directori de treball

# Especifica la ruta del fitxer .env per carregar les variables d'entorn
env_path = '/home/ubuntu/secure_card/bbdd_claves.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)  # Inicialitza l'aplicació Flask

# Obté les variables d'entorn per a la connexió a la base de dades
DATABASE = os.getenv('DB_DATABASE')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
FERNET_KEY = os.getenv('FERNET_KEY')

# Funció per a establir una connexió amb la base de dades
def get_db_connection():
    try:
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connectant a la base de dades: {err}", file=sys.stderr)
        return None

# Funció per a enregistrar un log d'accés a la base de dades
def registrar_log(id_targeta, puerta, acceso):
    db = get_db_connection()
    if db is None:
        print("Error connectant a la base de dades per a registrar logs.", file=sys.stderr)
        return

    cursor = db.cursor()
    try:
        query = "INSERT INTO logs (ID_Targeta_Log, Puerta, Acceso) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_targeta, puerta, int(acceso)))
        db.commit()
    except Exception as e:
        print(f"Error en registrar el log: {e}")
    finally:
        cursor.close()
        db.close()

# Ruta per a processar les dades rebudes a través d'una petició POST
@app.route('/procesar_datos', methods=['POST'])
def procesar_datos():
    numero_rfid = request.form.get('numero_rfid', '')  # Obté el número RFID de la petició POST
    puerta = request.form.get('puerta', '')  # Obté la porta de la petició POST

    if not re.match("^\d+$", numero_rfid):  # Comprova si el número RFID té un format vàlid
        registrar_log(numero_rfid, puerta, 0)  # Registra un log d'accés denegat a la base de dades
        return make_response("false\n", 200, {'Content-Type': 'text/plain'})

    try:
        db = get_db_connection()  # Estableix una connexió amb la base de dades
        cursor = db.cursor()

        cursor.execute("SELECT Estado, ID_Targeta FROM usuarios WHERE ID_Targeta = %s", (numero_rfid,))
        resultado = cursor.fetchone()  # Obté el primer resultat de la consulta

        if resultado is None or resultado[0] != 1:  # Comprova si la targeta està activa
            registrar_log(resultado[1], puerta, 0)  # Registra un log d'accés denegat a la base de dades
            return make_response("false\n", 200, {'Content-Type': 'text/plain'})

        estado, id_targeta = resultado
        acceso_concedido = True if estado == 1 else False  # Determina si s'ha concedit l'accés

        if acceso_concedido:
            cursor.execute("SELECT Nombre FROM usuarios WHERE ID_Targeta = %s", (numero_rfid,))
            nombre_usuario = cursor.fetchone()[0].strip().lower()
            hash_nombre = hashlib.sha256(nombre_usuario.encode()).hexdigest()  # Genera un hash del nom de l'usuari
            ruta_archivo_hash = os.path.join(DIRECTORIO, "hash.txt")
            with open(ruta_archivo_hash, "w") as archivo:
                archivo.write(hash_nombre)

            # Registra l'accés concedit al fitxer name_log.txt
            ruta_archivo_log = os.path.join(DIRECTORIO, "name_log.txt")
            with open(ruta_archivo_log, "w") as archivo_log:
                archivo_log.write(f"{numero_rfid}\n")
        else:
            registrar_log(id_targeta, puerta, 0)  # Registra un log d'accés denegat a la base de dades
    except Exception as e:
        print(f"Error en processar les dades: {e}")
        if resultado:
            registrar_log(resultado[1], puerta, 0)  # Registra un log d'accés denegat a la base de dades
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
