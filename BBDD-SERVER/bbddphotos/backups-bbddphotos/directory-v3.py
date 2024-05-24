from flask import Flask, request, redirect, url_for, send_from_directory, abort  # Importa els mòduls Flask necessaris
import os  # Importa el mòdul os per a funcions del sistema operatiu
from werkzeug.utils import secure_filename  # Importa la funció secure_filename del mòdul werkzeug per a noms de fitxers segurs
import zipfile  # Importa el mòdul zipfile per a manipulació d'arxius zip

# Inicialitza l'aplicació Flask
app = Flask(__name__)

# Defineix la carpeta d'enviament i la configura a l'aplicació Flask
UPLOAD_FOLDER = 'bbdd-directory'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Defineix les extensions de fitxers permeses
app.config['ALLOWED_EXTENSIONS'] = {'zip'}

# Funció per comprovar si l'extensió del fitxer és vàlida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ruta per a l'enviament de fitxers
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:  # Comprova si no s'ha enviat cap fitxer
        return redirect(request.url)  # Redirigeix a la mateixa pàgina
    file = request.files['file']  # Obté el fitxer enviat
    if file.filename == '' or not allowed_file(file.filename):  # Comprova si el fitxer té un nom vàlid o una extensió vàlida
        return redirect(request.url)  # Redirigeix a la mateixa pàgina
    if file:  # Si s'ha enviat un fitxer vàlid
        filename = secure_filename(file.filename)  # Obté un nom de fitxer segur
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Uneix la carpeta d'enviament amb el nom del fitxer
        file.save(filepath)  # Guarda el fitxer al servidor

        # Descomprimeix el fitxer
        with zipfile.ZipFile(filepath, 'r') as zip_ref:  # Obre el fitxer zip
            zip_ref.extractall(app.config['UPLOAD_FOLDER'])  # Extreu el contingut del fitxer zip a la carpeta d'enviament

        os.remove(filepath)  # Elimina el fitxer zip després de descomprimir-lo (opcional)
        return 'Fitxer carregat i descomprimit amb èxit.\n'  # Retorna un missatge d'èxit

# Ruta per a servir els fitxers carregats
@app.route('/photos/<path:filename>')
def serve_photo(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  # Serveix el fitxer des de la carpeta d'enviament
    except FileNotFoundError:
        abort(404)  # Si el fitxer no es troba, retorna un error 404

# Inicia l'aplicació Flask en mode de depuració
if __name__ == '__main__':
    app.run(debug=True)
