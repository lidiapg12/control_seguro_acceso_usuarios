ubuntu@BETA-PROJECT:~/photoproject$ cat app.py 
from flask import Flask, request, make_response
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)

@app.route('/photos/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return make_response("false\n", 400, {'Content-Type': 'text/plain'})
    file = request.files['file']
    if file.filename == '':
        return make_response("false\n", 400, {'Content-Type': 'text/plain'})
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('/home/ubuntu/photoproject/photos', filename)
        file.save(filepath)

        command = [
            '/usr/bin/python3.10',
            '/home/ubuntu/photoproject/face_recognition/reconocimiento_facial.py',
        ]

        environment = os.environ.copy()
        environment['PATH'] += os.pathsep + '/home/ubuntu/.local/bin'

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, env=environment)
            if result.stdout.strip():  # Verifica si hay una respuesta no vacía
                response = result.stdout.strip() + "\n"  # Añade un salto de línea al final
            else:
                response = "false\n"  # Incluye el salto de línea para consistencia
        except subprocess.CalledProcessError:
            response = "false\n"  # Incluye el salto de línea para consistencia

        # Devuelve la respuesta como texto plano, incluyendo el salto de línea
        return make_response(response, 200, {'Content-Type': 'text/plain'})

    else:
        return make_response("false\n", 500, {'Content-Type': 'text/plain'})

if __name__ == '__main__':
    app.run(debug=True)

