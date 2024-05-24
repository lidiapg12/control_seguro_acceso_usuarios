from flask import session
import mysql.connector
from werkzeug.security import check_password_hash

def login_usuario(username, password, db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM login_web WHERE usuario = %s', (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['usuario'] = username  # Establecer la sesión del usuario
            return True
        else:
            return False
    except Exception as e:
        print(f"Error en el inicio de sesión: {e}")
        return False
