#!/bin/env python3

# Importaciones necesarias para la aplicación
import re
from flask import Flask, request, jsonify, abort
import mysql.connector
from functools import wraps

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Lista de IPs permitidas
ALLOWED_IPS = ['44.196.115.21']  # Añade la IP de tu reverse proxy aquí

def ip_restriction(f):
    """
    Decorador que verifica si la solicitud proviene de una IP permitida.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            abort(403)  # Acceso prohibido si no es una IP permitida
        return f(*args, **kwargs)
    return decorated_function

def registrar_log(numero_rfid, acceso, desc='D'):
    """
    Función para registrar un intento de acceso en la tabla de logs.
    """
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="LQH",
            password="projecte.itb",
            database="beta"
        )
        cursor = db.cursor()
        query = "INSERT INTO logs (data_hora, num_targeta_logs, acces, targ_desc) VALUES (NOW(), %s, %s, %s)"
        cursor.execute(query, (numero_rfid, int(acceso), desc))
        db.commit()
    except Exception as e:
        print(f"Error al registrar log: {e}")
    finally:
        cursor.close()
        db.close()

@app.route('/procesar_datos', methods=['POST'])
@ip_restriction
def procesar_datos():
    """
    Endpoint para procesar solicitudes POST, validar el número de tarjeta RFID y registrar el intento en la base de datos.
    """
    numero_rfid = request.form.get('numero_rfid', '')
    desc = 'D'
    acceso_concedido = False
    nombre_usuario = False  # Cambiado de None a False

    if not re.match("^\d+$", numero_rfid):
        registrar_log(numero_rfid, acceso_concedido, desc)
        return jsonify(nombre_usuario)

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="LQH",
            password="projecte.itb",
            database="beta"
        )
        cursor = db.cursor()
        cursor.execute("SELECT Estat, id_user_targeta FROM targeta WHERE num_targeta = %s", (numero_rfid,))
        resultado = cursor.fetchone()

        if resultado is not None:
            estat, id_usuario = resultado
            desc = '-'
            if estat == 1:
                acceso_concedido = True
                cursor.execute("SELECT Nom FROM usuaris WHERE id_user = %s", (id_usuario,))
                nombre_usuario = cursor.fetchone()[0]

    except Exception as e:
        print(f"Error al procesar datos: {e}")
    finally:
        registrar_log(numero_rfid, acceso_concedido, desc)
        cursor.close()
        db.close()

    if nombre_usuario:
        return nombre_usuario + '\n'
    else:
        return jsonify(nombre_usuario)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
