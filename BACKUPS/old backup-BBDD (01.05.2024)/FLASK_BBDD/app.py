#!/bin/env python3

# Importacions necessàries per a l'aplicació
import re
from flask import Flask, request, jsonify, abort
import mysql.connector
from functools import wraps

# Inicialització de l'aplicació Flask
app = Flask(__name__)

# Llista d'IPs permeses
ALLOWED_IPS = ['***.***.***.**']  # Afegeix la IP del teu servidor invers aquí

def ip_restriction(f):
    """
    Decorador que verifica si la sol·licitud prové d'una IP permesa.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            abort(403)  # Accés prohibit si no és una IP permesa
        return f(*args, **kwargs)
    return decorated_function

def registrar_log(numero_rfid, accés, desc='D'):
    """
    Funció per a registrar un intent d'accés a la taula de registres.
    """
    try:
        db = mysql.connector.connect(
            host="**",
            user="**",
            password="**",
            database="**"
        )
        cursor = db.cursor()
        query = "INSERT INTO logs (data_hora, num_targeta_logs, acces, targ_desc) VALUES (NOW(), %s, %s, %s)"
        cursor.execute(query, (numero_rfid, int(acces), desc))
        db.commit()
    except Exception as e:
        print(f"Error en registrar el registre: {e}")
    finally:
        cursor.close()
        db.close()

@app.route('/procesar_datos', methods=['POST'])
@ip_restriction
def procesar_datos():
    """
    Endpoint per processar sol·licituds POST, validar el número de targeta RFID i registrar l'intent a la base de dades.
    """
    numero_rfid = request.form.get('numero_rfid', '')
    desc = 'D'
    accés_concedit = False

    if not re.match("^\d+$", numero_rfid):
        registrar_log(numero_rfid, accés_concedit, desc)
        return jsonify(acces_concedit)

    try:
        db = mysql.connector.connect(
            host="**",
            user="**",
            password="**",
            database="**"
        )
        cursor = db.cursor()
        cursor.execute("SELECT Estat FROM targeta WHERE num_targeta = %s", (numero_rfid,))
        resultat = cursor.fetchone()

        if resultat is not None:
            desc = '-'
            if resultat[0] == 1:
                accés_concedit = True
    except Exception as e:
        print(f"Error en processar les dades: {e}")
    finally:
        registrar_log(numero_rfid, accés_concedit, desc)
        cursor.close()
        db.close()

    return jsonify(acces_concedit)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
