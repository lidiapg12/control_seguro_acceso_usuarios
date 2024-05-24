from flask import Flask, request, make_response  # Importa funcions de Flask per a l'aplicació web
from werkzeug.utils import secure_filename  # Importa funcions per a assegurar noms de fitxers
import os  # Importa funcions del sistema operatiu
import subprocess  # Importa funcions per a executar processos externs
import hashlib  # Importa funcions per a realitzar hash
import mysql.connector  # Importa el connector MySQL per a Python
import sys  # Importa funcions i variables del sistema
from dotenv import load_dotenv  # Importa funció per a carregar variables d'entorn des d'un arxiu .env

# Càrrega les variables d'entorn des d'un arxiu .env
load_dotenv('/home/ubuntu/secure_card/bbdd_claves.env')

app = Flask(__name__)  # Crea una instància de l'aplicació Flask

# Defineix les variables d'entorn per a la connexió a la base de dades i al xifrat
DB_HOST = os.getenv('DB_HOST', '**')
DB_USER = os.getenv('DB_USER', '**')
DB_PASSWORD = os.getenv('DB_PASSWORD', '**')
DB_DATABASE = os.getenv('DB_DATABASE', '**')
FERNET_KEY = os.getenv('FERNET_KEY')

# Defineix els directoris i rutes de fitxers fixes per a l'execució
DIRECTORIO = "/home/ubuntu/myproject"
PHOTO_STORE_PATH = "/home/ubuntu/photoproject/photos"
PYTHON_PATH = "/usr/bin/python3.10"
RECOGNITION_SCRIPT_PATH = "/home/ubuntu/photoproject/face_recognition/reconocimiento_facial.py"

def get_db_connection():  # Funció per a connectar-se a la base de dades MySQL
    try:
        # Connecta amb la base de dades MySQL
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        return db
    except Exception as e:
        # Captura i imprimeix errors de connexió a la base de dades
        print(f"Error al conectar a la base de datos: {e}", file=sys.stderr)
        return None

def registrar_log(id_targeta, puerta, acceso):  # Funció per a registrar un log d'accés a la base de dades
    # Registra un log d'accés a la base de dades
    db = get_db_connection()
    if db is None:
        print("Failed to connect to database for logging.", file=sys.stderr)
        return

    cursor = db.cursor()
    try:
        # Executa una consulta SQL per inserir el log a la base de dades
        query = "INSERT INTO logs (ID_Targeta_Log, Puerta, Acceso) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_targeta, puerta, int(acceso)))
        db.commit()
    except Exception as e:
        # Captura i imprimeix errors en el registre del log
        print(f"Error al registrar log: {e}", file=sys.stderr)
    finally:
        cursor.close()
        db.close()

@app.route('/photos/upload', methods=['POST'])  # Ruta per a pujar fotos al servidor
def upload_file():
    puerta = request.form.get('puerta', '')  # Obté el número de porta de la sol·licitud HTTP

    if 'file' not in request.files:  # Comprova si s'ha proporcionat un fitxer
        # Retorna una resposta d'error si no s'ha proporcionat cap fitxer
        return make_response("false\n", 400, {'Content-Type': 'text/plain'})

    file = request.files['file']
    if file.filename == '':
        # Retorna una resposta d'error si el nom del fitxer és buit
        return make_response("false\n", 400, {'Content-Type': 'text/plain'})

    filename = secure_filename(file.filename)  # Assegura el nom del fitxer per a evitar vulnerabilitats
    filepath = os.path.join(PHOTO_STORE_PATH, filename)  # Obté la ruta completa del fitxer
    file.save(filepath)  # Guarda el fitxer en el servidor

    command = [PYTHON_PATH, RECOGNITION_SCRIPT_PATH]  # Defineix la comanda per a reconeixement facial

    environment = os.environ.copy()  # Còpia les variables d'entorn actuals
    environment['PATH'] += os.pathsep + '/home/ubuntu/.local/bin'  # Afegeix una nova ubicació al PATH

    try:
        # Executa un script de reconeixement facial per identificar el rostre a la foto
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=environment)
        if result.stdout.strip():
            # Si s'ha trobat un rostre vàlid, processa la informació
            directory_name = result.stdout.strip()
            directory_hash = hashlib.sha256(directory_name.encode()).hexdigest()
            hash_file_path = os.path.join(DIRECTORIO, "hash.txt")
            with open(hash_file_path, 'r') as hash_file:
                stored_hash = hash_file.read().strip()
            with open(os.path.join(DIRECTORIO, "name_log.txt"), 'r') as file:
                id_targeta = file.read().strip()

            if directory_hash.lower() == stored_hash:
                # Si la coincidència del hash és vàlida, es registra l'accés a la base de dades
                registrar_log(id_targeta, puerta, 1)
                return make_response(directory_name + "\n", 200, {'Content-Type': 'text/plain'})
            else:
                registrar_log(id_targeta, puerta, 0)
                return make_response("false\n", 200, {'Content-Type': 'text/plain'})
        else:
            registrar_log('', puerta, 0)
            return make_response("false\n", 200, {'Content-Type': 'text/plain'})
    except subprocess.CalledProcessError:
        # Captura i gestiona errors si el procés de reconeixement facial falla
        registrar_log('', puerta, 0)
        return make_response("false\n", 500, {'Content-Type': 'text/plain'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)  # Inicia l'aplicació Flask al servidor
