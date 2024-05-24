from flask import Flask, request, redirect, url_for, send_from_directory, abort  # Importació de mòduls necessaris
import os  # Importació del mòdul os per a funcions del sistema operatiu
from werkzeug.utils import secure_filename  # Importació de la funció per a noms de fitxers segurs
import zipfile  # Importació de la biblioteca per a manipulació de fitxers zip

app = Flask(__name__)  # Creació d'una nova instància de l'aplicació Flask
UPLOAD_FOLDER = 'bbdd-directory'  # Definició del directori on es carregaran i desaràn els fitxers
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configuració del directori d'uploads a l'aplicació
app.config['ALLOWED_EXTENSIONS'] = {'zip'}  # Extensions de fitxer permeses

def allowed_file(filename):
    # Funció per comprovar si l'extensió del fitxer està permesa
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']  # Comprovació de l'extensió

@app.route('/upload', methods=['POST'])
def upload_file():
    # Funció per carregar fitxers i desempaquetar-los
    if 'file' not in request.files:  # Comprovació si s'ha enviat un fitxer en la petició POST
        return redirect(request.url)  # Redirecció a la mateixa URL si no s'ha rebut cap fitxer
    file = request.files['file']  # Obtenció del fitxer enviat
    if file.filename == '' or not allowed_file(file.filename):  # Comprovació del nom del fitxer i extensió
        return redirect(request.url)  # Redirecció a la mateixa URL si el nom o extensió del fitxer no són vàlids
    if file:
        filename = secure_filename(file.filename)  # Obtenció d'un nom segur per al fitxer
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Creació de la ruta completa del fitxer
        file.save(filepath)  # Desament del fitxer en el directori d'uploads

        # Obtenció del nom del directori (sense l'extensió .zip)
        directory_name = os.path.splitext(filename)[0]  # Extreure el nom del fitxer sense l'extensió
        destination_directory = os.path.join(app.config['UPLOAD_FOLDER'], directory_name)  # Ruta del directori destí
        os.makedirs(destination_directory, exist_ok=True)  # Creació del directori de destí si no existeix

        # Descompressió del fitxer
        with zipfile.ZipFile(filepath, 'r') as zip_ref:  # Obertura del fitxer zip en mode de lectura
            zip_ref.extractall(destination_directory)  # Descompressió de tots els continguts al directori destí

        os.remove(filepath)  # Eliminació del fitxer .zip després de la descompressió (opcional)
        return 'Fitxer carregat i desempaquetat amb èxit.\n'  # Missatge de confirmació

@app.route('/photos/<path:filename>')
def serve_photo(filename):
    # Servei dels fitxers des de la carpeta d'uploads
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  # Servei del fitxer des del directori d'uploads
    except FileNotFoundError:
        abort(404)  # Abort de la petició amb codi d'estat 404 si el fitxer no es troba

if __name__ == '__main__':
    app.run(debug=True)  # Execució de l'aplicació en mode de depuració
