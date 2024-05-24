#!/bin/env python3 
"""
main.py
Quim Delgado
"""

import multiprocessing  # Importa la llibreria multiprocessing per gestionar processos múltiples
from time import sleep  # Importa la funció sleep de la llibreria time per a temporització
from rfid import readRfid, reader  # Importa funcions relacionades amb la lectura RFID
from camera import take_pic  # Importa la funció per capturar una foto
from i2c import instancia_display as display, bitmaps_dic  # Importa el display i els bitmaps
from buzzer_sound import instancia_buzzer as buzzer  # Importa el buzzer
from servo_movement import instancia_servo as servo  # Importa el servo

def read_rfid_with_multiprocessing(queue, old_key, new_key):
    """Funció per llegir RFID en un procés separa't."""
    respuestaServerID = readRfid(old_key, new_key)  # Llegeix l'ID RFID
    queue.put(respuestaServerID)  # Emmagatzema la resposta a la cua de comunicació

def take_pic_with_multiprocessing(queue):
    """Funció per capturar una foto en un procés separa't."""
    respuestaServerPIC = take_pic()  # Captura la foto
    queue.put(respuestaServerPIC)  # Emmagatzema la resposta a la cua de comunicació

def main():
    """Funció principal del programa."""
    recUser = False  # Inicialitza la variable de control de l'usuari reconegut
    print("LLIBRERIES CARREGADES")
    buzzer.select_song("La cucaracha")  # Reproduïx una melodia

    while not recUser:  # Repeteix fins que l'usuari sigui reconegut

        display.draw_bitmap(bitmaps_dic["insereix_targeta"])  # Mostra el missatge "Insereix la targeta"

        reader.read_id()  # Espera fins que el lector RFID llegeixi una targeta

        display.draw_bitmap(bitmaps_dic["no_retiris_targeta"])  # Mostra el missatge "No retiris la targeta"

        old_key, new_key = reader.get_keys()  # Obté les claus de la targeta llegida
        
        if old_key != 'false' or new_key != 'false':  # Verifica si les claus s'han llegit amb èxit
        
            # Crea cues per a la comunicació entre processos
            queue_rfid = multiprocessing.Queue()
            queue_pic = multiprocessing.Queue()

            # Inicia els dos processos
            process_rfid = multiprocessing.Process(target=read_rfid_with_multiprocessing, args=(queue_rfid,old_key,new_key))
            process_pic = multiprocessing.Process(target=take_pic_with_multiprocessing, args=(queue_pic,))
            process_rfid.start()
            process_pic.start()

            # Espera que els dos processos finalitzin
            process_rfid.join()
            process_pic.join()

            # Obté els resultats de les cues
            respuestaServerID = queue_rfid.get()
            respuestaServerPIC = queue_pic.get()

            display.clear_display()  # Esborra el contingut del display

            # Lògica per verificar i actuar segons les respostes rebudes
            if respuestaServerID != "false":  # Si l'ID RFID és vàlid
                if respuestaServerPIC != "false" and respuestaServerPIC is not None:  # Si s'ha capturat una foto vàlida
                        display.draw_text(f"Benvingude {respuestaServerPIC.capitalize()} has sigut validat")  # Mostra el missatge de benvinguda amb el nom de l'usuari
                        buzzer_sound = multiprocessing.Process(target=buzzer.select_song, args=("Game Of Thrones",))  # Reproduïx la melodia "Game Of Thrones" en un procés separat
                        servo_door = multiprocessing.Process(target=servo.open_door)  # Obre la porta amb el servo en un procés separat
                        buzzer_sound.start()
                        servo_door.start()
                        buzzer_sound.join()
                        servo_door.join()
                else:
                    display.draw_bitmap(bitmaps_dic["usuari_invalid"])  # Mostra el missatge "Usuari invàlid" si no s'ha capturat una foto vàlida
                    buzzer.select_song("Fail")  # Reproduïx un senyal d'error amb el buzzer
            else:
                display.draw_bitmap(bitmaps_dic["usuari_invalid"])  # Mostra el missatge "Usuari invàlid" si l'ID RFID no és vàlid
                buzzer.select_song("Fail")  # Reproduïx un senyal d'error amb el buzzer
        else:
            display.draw_bitmap(bitmaps_dic["usuari_invalid"])  # Mostra el missatge "Usuari invàlid" si no s'han pogut llegir les claus de la targeta
            buzzer.select_song("Fail")  # Reproduïx un senyal d'error amb el buzzer

        sleep(2)  # Pausa de 2 segons
        display.draw_bitmap(bitmaps_dic["retira_targeta"])  # Mostra el missatge "Retira la targeta"
        sleep(10)  # Pausa de 10 segons

try:
    main()  # Executa la funció principal del programa
except Exception as e:
    print(f"Error: {e}")
finally:
    display.clear_display()  # Esborra el contingut del display al sortir del programa
