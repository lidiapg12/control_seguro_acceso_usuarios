#!/usr/bin/env python3
"""
send.py
Quim Delgado
"""

import subprocess
from cryptography.fernet import Fernet

# Funció per rebre les claus de la targeta RFID del servidor
def recieveKeys(uid):
    uid = str(uid).replace(" ", "")  # Elimina els espais del UID
    print(f"UID: {uid}")
    try:
        # Realitza una sol·licitud POST al servidor per obtenir les claus
        resposta_enc = subprocess.run(['curl', '-X', 'POST', 'https://beta-bbdd.duckdns.org/secure', '-d', f'id={uid}&puerta=1'], capture_output=True, text=True)
        
        if resposta_enc.returncode == 0:  # Comprova si la sol·licitud ha estat exitosa
            resposta_enc = resposta_enc.stdout.strip()  # Elimina els espais del resultat
            resposta_enc = resposta_enc.replace(" ", "")  # Elimina els espais del resultat
            
            if resposta_enc == 'false':  # Comprova si la resposta és 'false'
                return "false"  # Retorna 'false'
            
            FERNET_KEY = b'qXKgjhxOGQ6HwZza83YpzJHe82eaiuUVCU4oIY6ZyoI='  # Clau Fernet per desxifrar
            fernet = Fernet(FERNET_KEY)  # Instancia un objecte Fernet
            resposta = fernet.decrypt(resposta_enc)  # Desxifra la resposta
            print(f"Decripted keys: {resposta}")  # Mostra les claus desxifrades
            resposta = resposta.decode('ascii')  # Decodifica la resposta en ASCII
            return resposta  # Retorna la resposta
        
        else:
            print("Error en la solicitud:", resposta_enc.stderr)  # Mostra un missatge d'error si hi ha problemes amb la sol·licitud
            return "false"  # Retorna 'false' en cas d'error
        
    finally:
        print()  # Imprimeix una línia en blanc

# Funció per enviar l'ID al servidor
def sendToServerID(text):
    text = text.split()[0]  # Assumeix que vols el primer element del text dividit
    try:
        # Realitza una sol·licitud POST al servidor per enviar l'ID
        response = subprocess.run(['curl', '-X', 'POST', 'https://beta-bbdd.duckdns.org/procesar_datos', '-d', f'numero_rfid={text}&puerta=1'], capture_output=True, text=True)
        
        if response.returncode == 0:  # Comprova si la sol·licitud ha estat exitosa
            text_response = response.stdout.strip()  # Elimina els espais del resultat
            text_response = text_response.replace(" ", "")  # Elimina els espais del resultat si és necessari
            return text_response  # Retorna la resposta
        else:
            print("Error en la solicitud:", response.stderr)  # Mostra un missatge d'error si hi ha problemes amb la sol·licitud
            return "false"  # Retorna 'false' en cas d'error
    except Exception as e:
        print(f"Error al enviar l'ID amb subprocess: {e}")  # Mostra un missatge d'error en cas d'excepció
        return "false"  # Retorna 'false' en cas d'error

# Funció per enviar una imatge al servidor
def sendToServerPIC(nom_foto):
    """Envia una imatge al servidor utilitzant curl."""
    try:
        # Realitza una sol·licitud POST al servidor per enviar la imatge
        response = subprocess.run(['curl', '-X', 'POST', '-F', f'file=@{nom_foto}', '-F', 'puerta=1', 'https://beta-bbdd.duckdns.org/photos/upload'], capture_output=True, text=True)

        if response.returncode == 0:  # Comprova si la sol·licitud ha estat exitosa
            text_response = response.stdout.strip()  # Elimina els espais del resultat
            text_response = text_response.replace(" ", "")  # Elimina els espais del resultat si és necessari
            return text_response  # Retorna la resposta
        else:
            print("Error enviant la imatge:", response.stderr)  # Mostra un missatge d'error si hi ha problemes amb la sol·licitud
            return "false"  # Retorna 'false' en cas d'error
    except Exception as e:
        print(f"Error al enviar la imatge amb subprocess: {e}")  # Mostra un missatge d'error en cas d'excepció
        return "false"  # Retorna 'false' en cas d'error

if __name__ == '__main__':
    # Prova les funcions amb un UID concret
    recieveKeys(uid='1061384018777')
