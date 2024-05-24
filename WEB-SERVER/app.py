from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import check_password_hash
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import redirect, url_for, session
from dotenv import load_dotenv
import subprocess
import requests




from static.function.usuarios import obtener_usuarios, obtener_tarjetas, obtener_logs, obtener_accesos
from static.function.inserts import insertar_usuario, insertar_clave, insertar_acceso, subir_archivo_zip
from static.function.login import login_usuario
from static.function.eliminar import eliminar_usuario_db
from static.function.modificar import actualizar_estado_tarjeta, actualizar_clave_db, actualizar_accesos
from static.function.dashboard import contar_usuarios, obtener_accesos_por_usuario, obtener_accesos_por_puerta


app = Flask(__name__, template_folder='template')

# Configuración de la clave secreta
app.secret_key = os.getenv('FLASK_SECRET_KEY', '5452237d287cb99b393ffdb6433cc955')

# Configuración del registro de Flask
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
log_handler = RotatingFileHandler('/var/log/flask/app.log', maxBytes=1024*1024, backupCount=10)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

# Cargar variables de entorno desde el archivo entorno.env
load_dotenv(os.path.join(os.path.dirname(__file__), 'entorno.env'))

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

app.secret_key = os.getenv('FLASK_SECRET_KEY')

#LOGIN

from werkzeug.security import generate_password_hash

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']

        if login_usuario(username, password, db_config):
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña inválidos.'

    return render_template('login.html', error=error)



@app.route('/dashboard')
def dashboard():
    # Lógica para obtener los datos del dashboard, incluyendo el número de usuarios
    num_usuarios = contar_usuarios()  # Utiliza la función para contar usuarios
    accesos_por_usuario = obtener_accesos_por_usuario()  # Obtener datos de accesos por usuario
    accesos_por_puerta = obtener_accesos_por_puerta()  # Obtener datos de accesos por puerta
    # Otras operaciones para obtener más datos del dashboard
    return render_template('dashboard.html', num_usuarios=num_usuarios, 
                           accesos_por_usuario=accesos_por_usuario, 
                           accesos_por_puerta=accesos_por_puerta)



#LOGOUT

@app.route('/logout')
def logout():
    # Eliminar la sesión del usuario
    session.clear()
    # Redirigir al usuario a la página de inicio de sesión
    return redirect(url_for('login'))

#CONSULTAS

@app.route('/consultar')
def consultar():
    return render_template('consultar.html')

@app.route('/usuarios')
def vista_usuarios():
    datos = obtener_usuarios(db_config)  # Asegúrate de pasar db_config
    return render_template('consultar.html', datos=datos, tipo='usuarios')

@app.route('/tarjetas')
def vista_tarjetas():
    datos = obtener_tarjetas(db_config)
    return render_template('consultar.html', datos=datos, tipo='tarjetas')

@app.route('/logs')
def vista_logs():
    datos = obtener_logs(db_config)
    return render_template('consultar.html', datos=datos, tipo='logs')

@app.route('/accesos')
def vista_accesos():
    datos = obtener_accesos(db_config)
    return render_template('consultar.html', datos=datos, tipo='accesos')

#MODIFICAR USUARIOS

@app.route('/modificar')
def modificar():
    return render_template('modificar.html')

@app.route('/cambiar_estado_tarjeta', methods=['POST'])
def cambiar_estado_tarjeta():
    id_usuario = request.form.get('id_usuario')  # Asumiendo que cambias el formulario para enviar este ID
    nuevo_estado = request.form.get('nuevo_estado')

    result, success = actualizar_estado_tarjeta(id_usuario, nuevo_estado)
    flash(result, 'success' if success else 'error')
    return redirect(url_for('modificar'))  # Asegúrate de redirigir a la vista adecuada


@app.route('/actualizar_clave', methods=['POST'])
def actualizar_clave():
    id_usuario = request.form['id_usuari']
    nueva_clave = request.form['nueva_clave']
    result, success = actualizar_clave_db(id_usuario, nueva_clave)
    flash(result, 'success' if success else 'error')
    return redirect(url_for('modificar'))

@app.route('/modificar_accesos', methods=['POST'])
def modificar_accesos():
    id_usuario_acceso = request.form['id_usuario_acceso']
    puerta_1 = 1 if 'puerta_1' in request.form else 0
    puerta_2 = 1 if 'puerta_2' in request.form else 0
    puerta_3 = 1 if 'puerta_3' in request.form else 0
    puerta_4 = 1 if 'puerta_4' in request.form else 0
    puerta_5 = 1 if 'puerta_5' in request.form else 0

    result, success = actualizar_accesos(id_usuario_acceso, puerta_1, puerta_2, puerta_3, puerta_4, puerta_5)
    flash(result, 'success' if success else 'error')
    return redirect(url_for('modificar'))


# INSERTAR DATOS TABLA

@app.route('/insertar')
def insertar():
    return render_template('insertar.html')

@app.route('/insertar_todo', methods=['POST'])
def insertar_todo():
    if request.method == 'POST':
        # Dades d'usuari, clau, i accés
        id_targeta = request.form['id_targeta']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        estado = request.form['estado']
        clave_id = request.form['clave_id']
        clave = request.form['clave']
        puerta_1 = request.form['puerta_1']
        puerta_2 = request.form['puerta_2']
        puerta_3 = request.form['puerta_3']
        puerta_4 = request.form['puerta_4']
        puerta_5 = request.form['puerta_5']

        # Obtenció i enviament de l'arxiu ZIP
        archivo_zip = request.files.get('archivo_zip')

        try:
            if archivo_zip:
                subir_archivo_zip(archivo_zip)
                #flash("Archivo ZIP subido correctamente", "success")
            else:
                flash("Por favor, sube un archivo .zip", "error")

            id_usuario = insertar_usuario(id_targeta, nombre, apellido, estado)
            if id_usuario:
                insertar_clave(id_usuario, clave_id, clave)
                insertar_acceso(id_usuario, puerta_1, puerta_2, puerta_3, puerta_4, puerta_5)
                flash("Todos los datos han sido insertados correctamente", "success")
            else:
                flash("No se pudo insertar el usuario", "error")
        except Exception as e:
            flash(str(e), "error")
        
        return redirect(url_for('insertar'))

    return redirect(url_for('insertar'))  # Redirige a la página eliminar.html




#ELIMINAR DATOS

@app.route('/eliminar')
def eliminar():
    return render_template('eliminar.html')



@app.route('/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    user_id = request.form['userId']
    if user_id:
        resultado = eliminar_usuario_db(user_id)
        if resultado:
            flash('Usuario eliminado', 'success')  # Mensaje de éxito
        else:
            flash('Error al eliminar usuario', 'error')  # Mensaje de error
    else:
        flash('No se proporcionó un ID válido.', 'error')

    return redirect(url_for('eliminar'))  # Redirige a la página eliminar.html



if __name__ == '__main__':
    app.run(debug=True)
