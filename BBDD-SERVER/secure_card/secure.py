from flask import Flask, request  # Importa Flask per a la creació d'aplicacions web i request per a manejar les peticions HTTP
import mysql.connector  # Importa mysql.connector per a la connexió amb la base de dades MySQL
import sys  # Importa el mòdul sys per a les operacions del sistema
import random  # Importa el mòdul random per a la generació de nombres aleatoris
from cryptography.fernet import Fernet  # Importa Fernet de la biblioteca cryptography per al xifratge
import os  # Importa el mòdul os per a les operacions del sistema operatiu
from dotenv import load_dotenv  # Importa la funció load_dotenv per a carregar les variables d'entorn des d'un arxiu .env

# Cargar variables de entorno
env_path = '/home/ubuntu/secure_card/bbdd_claves.env'  # Defineix la ruta de l'arxiu .env
load_dotenv(dotenv_path=env_path)  # Carrega les variables d'entorn des de l'arxiu .env

app = Flask(__name__)  # Crea una instància de l'aplicació Flask

# Variables de entorn per a la connexió a la base de dades i el xifratge
DATABASE = os.getenv('DB_DATABASE')  # Obté el nom de la base de dades des de les variables d'entorn
USER = os.getenv('DB_USER')  # Obté l'usuari de la base de dades des de les variables d'entorn
PASSWORD = os.getenv('DB_PASSWORD')  # Obté la contrasenya de la base de dades des de les variables d'entorn
HOST = os.getenv('DB_HOST')  # Obté l'amfitrió de la base de dades des de les variables d'entorn
FERNET_KEY = os.getenv('FERNET_KEY').encode()  # Obté la clau de Fernet des de les variables d'entorn i la converteix a bytes

# Funció per a establir la connexió amb la base de dades
def get_db_connection():
    try:
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)  # Connecta a la base de dades MySQL
        return conn  # Retorna la connexió establerta
    except mysql.connector.Error as err:  # Captura els errors de connexió amb la base de dades
        print(f"Error connecting to the database: {err}", file=sys.stderr)  # Imprimeix l'error al fitxer de registre d'errors
        return None  # Retorna None si no es pot establir la connexió

# Funció per a registrar els intents fallits d'accés a la base de dades
def log_failed_access(id_targeta, puerta):
    conn = get_db_connection()  # Obre una connexió amb la base de dades
    if conn is None:  # Verifica si no s'ha pogut connectar a la base de dades
        print("Failed to connect to database for logging.", file=sys.stderr)  # Imprimeix un missatge d'error
        return  # Surte de la funció si no es pot establir la connexió

    cursor = conn.cursor()  # Crea un cursor per a la base de dades
    try:
        cursor.execute("""
            INSERT INTO logs (ID_Targeta_Log, Puerta, Acceso)
            VALUES (%s, %s, 0);
            """, (id_targeta, puerta))  # Executa la consulta SQL per a registrar l'intent fallit d'accés
        conn.commit()  # Confirma els canvis a la base de dades
    except mysql.connector.Error as err:  # Captura els errors SQL
        print(f"SQL error while logging failed access: {err}", file=sys.stderr)  # Imprimeix l'error al fitxer de registre d'errors
    finally:
        cursor.close()  # Tanca el cursor
        conn.close()  # Tanca la connexió amb la base de dades

# Ruta de l'aplicació per a gestionar les sol·licituds POST per a la targeta segura
@app.route("/secure", methods=['POST'])
def secure_card():
    id_targeta = request.form.get('id')  # Obté l'ID de la targeta de la sol·licitud POST
    puerta = request.form.get('puerta')  # Obté el número de la porta de la sol·licitud POST

    if not id_targeta or not puerta:  # Comprova si no s'ha rebut l'ID de la targeta o el número de la porta
        return "false\n"  # Retorna "false" si falten paràmetres

    conn = get_db_connection()  # Obre una connexió amb la base de dades
    if conn is None:  # Comprova si no s'ha pogut connectar a la base de dades
        return "false", 500  # Retorna "false" amb un codi d'estat HTTP 500 (Error del servidor)

    cursor = conn.cursor()  # Crea un cursor per a la base de dades

    try:
        # Verifica si l'ID de la targeta es troba a la taula claus_targeta
        cursor.execute("SELECT ID_usuari_Key FROM claves_targeta WHERE ID = %s;", (id_targeta,))
        id_usuari_resultat = cursor.fetchone()

        if id_usuari_resultat is None:  # Comprova si no s'ha trobat cap coincidència per a l'ID de la targeta
            return "false\n"  # Retorna "false" si l'ID de la targeta no es troba a la base de dades

        id_usuari = id_usuari_resultat[0]  # Obté l'ID de l'usuari associat a l'ID de la targeta

        # Obté l'ID de la targeta associada a l'usuari
        cursor.execute("SELECT ID_Targeta FROM usuaris WHERE ID_Usuario = %s;", (id_usuari,))
        id_targeta_usuari_resultat = cursor.fetchone()

        if id_targeta_usuari_resultat is None:  # Comprova si no s'ha trobat cap coincidència per a l'ID de l'usuari
            return "false\n"  # Retorna "false" si no s'ha trobat cap ID de targeta associat a l'usuari

        id_targeta_usuari = id_targeta_usuari_resultat[0]  # Obté l'ID de la targeta associada a l'usuari

        # Verifica l'estat de la targeta a la taula usuaris
        cursor.execute("SELECT Estado FROM usuaris WHERE ID_Usuario = %s;", (id_usuari,))
        resultat_estat = cursor.fetchone()

        if resultat_estat is None or resultat_estat[0] == 0:  # Comprova si l'estat de la targeta és 0 o no es troba a la base de dades
            log_failed_access(id_targeta_usuari, puerta)  # Registra un intent fallit d'accés a la base de dades
            return "false\n"  # Retorna "false" si l'estat de la targeta és 0 o no es troba a la base de dades

        # Verifica si l'usuari té accés a la porta a la taula accessos
        columna_puerta = f'Puerta_{puerta}'  # Obté el nom de la columna de la porta
        cursor.execute(f"SELECT {columna_puerta} FROM accesos WHERE ID_Usuario_Acceso = %s;", (id_usuari,))
        resultat_acces = cursor.fetchone()

        if resultat_acces is None or resultat_acces[0] != 1:  # Comprova si l'usuari té accés a la porta
            log_failed_access(id_targeta_usuari, puerta)  # Registra un intent fallit d'accés a la base de dades
            return "false\n"  # Retorna "false" si l'usuari no té accés a la porta

        # Obté la clau actual de la targeta de la taula claus_targeta
        cursor.execute("SELECT Clave FROM claves_targeta WHERE ID = %s;", (id_targeta,))
        clau_actual_resultat = cursor.fetchone()

        if clau_actual_resultat is None:  # Comprova si no s'ha trobat cap clau per a l'ID de la targeta
            return "false\n"  # Retorna "false" si no s'ha trobat cap clau per a l'ID de la targeta

        clau_actual = clau_actual_resultat[0]  # Obté la clau actual de la targeta

        # Genera una nova clau i xifra tant la clau actual com la nova
        nova_clau = str(random.randint(100000, 999999))  # Genera una nova clau aleatòria
        claus = f"{clau_actual}:{nova_clau}"  # Combina la clau actual i la nova clau
        cipher_suite = Fernet(FERNET_KEY)  # Inicialitza Fernet amb la clau de xifratge
        claus_xifrades = cipher_suite.encrypt(claus.encode()).decode()  # Xifra les claus

        # Actualitza la clau a la base de dades
        cursor.execute("UPDATE claves_targeta SET Clave = %s WHERE ID = %s;", (nova_clau, id_targeta))
        conn.commit()  # Confirma els canvis a la base de dades

        return claus_xifrades + "\n"  # Retorna les claus xifrades
    except mysql.connector.Error as err:  # Captura els errors SQL
        print(f"SQL error: {err}", file=sys.stderr)  # Imprimeix l'error al fitxer de registre d'errors
        return "false", 500  # Retorna "false" amb un codi d'estat HTTP 500 (Error del servidor)
    finally:
        cursor.close()  # Tanca el cursor
        conn.close()  # Tanca la connexió amb la base de dades

# Inicia l'aplicació Flask
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')  # Executa l'aplicació en mode de producció a totes les interfícies de xarxa
