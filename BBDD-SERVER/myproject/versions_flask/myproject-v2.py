#!/bin/env python3  # Indica la ruta de l'intèrpret Python a utilitzar

import re  # Importa el mòdul re per a expressions regulars
import os  # Importa el mòdul os per a funcions del sistema operatiu
import hashlib  # Importa el mòdul hashlib per a funcions de hash
from flask import Flask, request, make_response  # Importa classes necessàries de Flask
import mysql.connector  # Importa el connector MySQL per a la connexió amb la base de dades

app = Flask(__name__)  # Inicialitza l'aplicació Flask

DIRECTORIO = "/home/ubuntu/myproject"  # Defineix el directori

# Funció per obtenir una connexió a la base de dades
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="**",
            user="**",
            password="**",
            database="**"
        )
        return db
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
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

    try:
        db = mysql.connector.connect(
            host="**",
            user="**",
            password="**",
            database="**"
        )
        cursor = db.cursor()

        cursor.execute("SELECT Estado, ID_Targeta FROM usuarios WHERE ID_Targeta = %s", (numero_rfid,))
        resultado = cursor.fetchone()

        if resultado is None or resultado[0] != 1:  # Comprova si la targeta està activa
            registrar_log(resultado[1], puerta, 0)  # Registra un log d'accés denegat
            return make_response("false\n", 200, {'Content-Type': 'text/plain'})

        estado, id_targeta = resultado
        acceso_concedido = True if estado == 1 else False

        if acceso_concedido:  # Si s'ha concedit l'accés
            cursor.execute("SELECT Nombre FROM usuarios WHERE ID_Targeta = %s", (numero_rfid,))
            nombre_usuario = cursor.fetchone()[0].strip().lower()
            hash_nombre = hashlib.sha256(nombre_usuario.encode()).hexdigest()  # Genera un hash del nom de l'usuari
            ruta_archivo = os.path.join(DIRECTORIO, "hash.txt")
            with open(ruta_archivo, "w") as archivo:
                archivo.write(hash_nombre)
        else:
            registrar_log(id_targeta, puerta, 0)  # Registra un log d'accés denegat
    except Exception as e:
        print(f"Error al procesar datos: {e}")
        if resultado:
            registrar_log(resultado[1], puerta, 0)  # Registra un log d'accés denegat
        return make_response("Internal Server Error\n", 500)
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
