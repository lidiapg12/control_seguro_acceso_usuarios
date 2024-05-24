#!/usr/bin/env python3
"""
camera.py
Quim Delgado
"""

import time  # Importa la llibreria time per treballar amb temps
import cv2  # Importa la llibreria OpenCV per al processament d'imatges
import os  # Importa la llibreria os per a funcions relacionades amb el sistema operatiu
import threading  # Importa la llibreria threading per treballar amb fils
from buzzer_sound import instancia_buzzer as buzzer  # Importa l'objecte instancia_buzzer de buzzer_sound.py
from send import sendToServerPIC  # Importa la funció sendToServerPIC de send.py
from i2c import bitmaps_dic, instancia_display as display  # Importa el diccionari bitmaps_dic i l'objecte instancia_display de i2c.py

def show_pic_in_background(nom_foto):
    """Funció per mostrar la imatge en el display en un fil separat."""
    display.show_image(nom_foto)  # Mostra la imatge en el display en un fil separat

def user_signals():
    for i in range(3, 0, -1):
        display.draw_text("  " + str(i), font_size=50)  # Dibuixa el text del compte enrere
        time.sleep(0.3)  # Pausa de 0.3 segons
    display.draw_bitmap(bitmaps_dic["xis"])  # Dibuixa un bitmap d'un símbol de X

def preparar_cam(cap):
    for i in range(3, 0, -1):
        cap.read()  # Llegeix un frame de la càmera per preparar-la
        time.sleep(0.3)  # Pausa de 0.3 segons

def take_pic(nom_foto="foto_capturada.jpg"):
    display.clear_display()  # Esborra el display
    display.draw_bitmap(bitmaps_dic["mira_a_la_camara"])  # Dibuixa un bitmap d'una icona de "Mira a la càmera"
    cap = cv2.VideoCapture('/dev/video0')  # Inicia la captura de vídeo de la càmera especificada

    user_signals_thread = threading.Thread(target=user_signals)  # Inicia un fil per mostrar senyals a l'usuari
    preparar_cam_thread = threading.Thread(target=preparar_cam, args=(cap,))  # Inicia un fil per preparar la càmera

    if not cap.isOpened():  # Verifica si la càmera s'ha obert correctament
        print("No s'ha pogut obrir la càmera.")
        return "false"

    time.sleep(2)  # Pausa de 2 segons

    user_signals_thread.start()  # Inicia el fil que mostra senyals a l'usuari
    preparar_cam_thread.start()  # Inicia el fil per preparar la càmera
    user_signals_thread.join()  # Espera a que el fil que mostra senyals a l'usuari acabi
    preparar_cam_thread.join()  # Espera a que el fil per preparar la càmera acabi

    ret, frame = cap.read()  # Captura un frame

    buzzer.select_song("Foto")  # Reprodueix una melodia per indicar que s'ha fet una foto

    if ret:
        cv2.imwrite(nom_foto, frame)  # Guarda la imatge capturada amb el nom especificat
        threading.Thread(target=show_pic_in_background, args=(nom_foto,)).start()  # Mostra la imatge en el display en un fil separat
        print("Enviant foto")
        respostaServerPIC = sendToServerPIC(nom_foto)  # Envia la foto al servidor en el fil principal i obté una resposta

        # os.remove(nom_foto)  # Elimina la foto capturada

        return respostaServerPIC
    else:
        print("Error al capturar la foto")

    cap.release()  # Assegura que la captura es tanqui independentment del resultat

if __name__ == "__main__":
    try:
        print("Presiona Ctrl+C per sortir")
        while 1:
            input("Enter per fer foto: ")
            take_pic()

    except KeyboardInterrupt:
        display.clear_display()
    finally:
        display.clear_display()
