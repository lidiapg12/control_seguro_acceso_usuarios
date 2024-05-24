#VERSIÓ ANTIGA DE LA APP. BACKUP. 

#!/bin/env python3

# Importacions necessàries per a l'aplicació
import re  # Utilitzat per validar el format dels números RFID mitjançant expressions regulars.
from flask import Flask, request, jsonify  # Flask per crear l'aplicació web i gestionar les sol·licituds.
import mysql.connector  # Connector de MySQL per a operacions de base de dades.
from mysql.connector import errorcode  # Mòdul per identificar errors específics de MySQL.

# Inicialització de l'aplicació Flask
app = Flask(__name__)

def registrar_log(numero_rfid, acceso, desc='D'):
    """
    Funció per enregistrar un intent d'accés a la taula de logs.

    Args:
        numero_rfid (str): El número de la targeta RFID.
        acceso (bool): Indica si l'accés ha estat concedit (True) o denegat (False).
        desc (str): Descripció de l'intent. '-' si la targeta existeix al sistema,
                    'D' si la targeta no existeix o està inactiva.
    """
    try:
        # Connexió a la base de dades
        db = mysql.connector.connect(
            host="*",  # Adreça del servidor de la base de dades
            user="*",  # Usuari de la base de dades
            password="*",  # Contrasenya de l'usuari
            database="*"  # Nom de la base de dades
        )
        cursor = db.cursor()
        # Consulta SQL per inserir el registre a la taula de logs
        query = "INSERT INTO logs (data_hora, num_targeta_logs, acces, targ_desc) VALUES (NOW(), %s, %s, %s)"
        cursor.execute(query, (numero_rfid, int(acceso), desc))  # Execució de la consulta
        db.commit()  # Confirmació de la transacció
    except Exception as e:
        # Gestió d'errors en el registre del log
        print(f"Error en registrar el log: {e}")
    finally:
        # Tancament del cursor i la connexió a la base de dades
        cursor.close()
        db.close()

@app.route('/procesar_datos', methods=['POST'])
def procesar_datos():
    """
    Endpoint per processar sol·licituds POST, validar el número de targeta RFID i enregistrar l'intent a la base de dades.

    Returns:
        JSON response: Resposta en format JSON indicant si l'accés ha estat concedit (True) o denegat (False).
    """
    numero_rfid = request.form.get('numero_rfid', '')
    desc = 'D'  # Suposem inicialment que la targeta no està al sistema
    acceso_concedido = False

    if not re.match("^\d+$", numero_rfid):
        # Si el format del número RFID no és vàlid, registra l'intent com a fallit
        registrar_log(numero_rfid, acceso_concedido, desc)
        return jsonify(acceso_concedido)

    try:
        # Connexió a la base de dades
        db = mysql.connector.connect(
            host="*",
            user="*",
            password="*",
            database="*"
        )
        cursor = db.cursor()
        # Consulta per verificar l'existència i l'estat de la targeta
        cursor.execute("SELECT Estat FROM targeta WHERE num_targeta = %s", (numero_rfid,))
        resultado = cursor.fetchone()

        if resultado is not None:
            desc = '-'  # La targeta existeix al sistema
            if resultado[0] == 1:
                acceso_concedido = True  # Accés concedit si la targeta està activa
    except Exception as e:
        # Gestió d'errors durant el processament de dades
        print(f"Error al processar les dades: {e}")
    finally:
        # Registra l'intent amb els detalls obtinguts i tanca els recursos de la BD
        registrar_log(numero_rfid, acceso_concedido, desc)
        cursor.close()
        db.close()

    # Resposta indicant si l'accés ha estat concedit o denegat
    return jsonify(acceso_concedido)

# Punt d'entrada principal que inicia l'aplicació Flask si aquest script s'executa directament
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

