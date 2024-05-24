import RPi.GPIO as GPIO  # Importa la biblioteca GPIO de Raspberry Pi
GPIO.setwarnings(False)  # Desactiva els avisos del GPIO
GPIO.cleanup()  # Restableix la configuració del GPIO
GPIO.setmode(GPIO.BCM)  # Estableix el mode de numeració dels pins GPIO

from mfrc522 import MFRC522  # Importa la classe MFRC522 per a la comunicació RFID
from send import recieveKeys, sendToServerID  # Importa les funcions per a enviar dades al servidor
import time  # Importa la llibreria de temps de Python
import random  # Importa la llibreria random de Python

# Classe per gestionar la comunicació RFID
class RFID:
    def __init__(self):
        self.reader = MFRC522()  # Inicialitza el lector MFRC522

    # Mètode per definir els blocs de memòria d'una determinada regió (sector)
    def define_block(self, sector=1):
        block_addrs = [sector * 4 + i for i in range(3)]  # Calcula les adreces dels blocs de dades
        trailer = sector * 4 + 3  # Calcula l'adreça del bloc de control
        return block_addrs, trailer

    # Mètode per convertir l'identificador UID de la targeta RFID a un número
    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

    # Mètode per llegir l'ID d'una targeta RFID
    def read_id(self):
        id = None
        while not id:
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    return self.uid_to_num(uid)

    # Mètode per llegir dades d'una targeta RFID
    def read(self, block_addrs, trailer, key):
        id = None
        while not id:
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    id = self.uid_to_num(uid)
                    self.reader.MFRC522_SelectTag(uid)
                    status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1B, trailer, key, uid)
                    data = []
                    text_read = ''
                    if status == self.reader.MI_OK:
                        for block_num in block_addrs:
                            block = self.reader.MFRC522_Read(block_num)
                            if block:
                                data += block
                        if data:
                            text_read = ''.join(chr(i) for i in data)
                    self.reader.MFRC522_StopCrypto1()
        return id, text_read

    # Mètode per escriure dades en una targeta RFID
    def write(self, block_addrs, trailer, old_key, text):
        id = None
        while not id:
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    id = self.uid_to_num(uid)
                    self.reader.MFRC522_SelectTag(uid)
                    status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1B, trailer, old_key, uid)
                    self.reader.MFRC522_Read(trailer)
                    if status == self.reader.MI_OK:
                        data = bytearray(text.ljust(len(block_addrs) * 16).encode('ascii'))
                        for i, block_num in enumerate(block_addrs):
                            self.reader.MFRC522_Write(block_num, data[(i * 16): (i + 1) * 16])
                    self.reader.MFRC522_StopCrypto1()
                    return id, text[0:(len(block_addrs) * 16)]

    # Mètode per canviar les claus d'autenticació d'una targeta RFID
    def change_keys(self, trailer, old_key, new_key):
        id = None
        while not id:
            access_bits = [0x0F, 0x00, 0xFF, 0x69]  # Configura els bits d'accés
            buffer = new_key + access_bits + new_key
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    id = self.uid_to_num(uid)
                    self.reader.MFRC522_SelectTag(uid)
                    status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1B, trailer, old_key, uid)
                    if status == self.reader.MI_OK:
                        self.reader.MFRC522_Write(trailer, buffer)
                        print("Sector trailer configured successfully.")
                    else:
                        print("Authentication error when setting sector trailer.")
                    self.reader.MFRC522_StopCrypto1()
        return id

    # Mètode per obtenir les claus de la targeta RFID des del servidor
    def get_keys(self):
        id = None
        while not id:
            print("Waiting for card...")
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    GPIO.cleanup()
                    keys = recieveKeys(self.uid_to_num(uid))
                    if keys != 'false':
                        # Format Keys
                        print("Keys: ", keys)
                        if keys != 'false':
                            old_key = [ord(keys[i]) for i in range(6)]
                            new_key = [ord(keys[i]) for i in range(7, 13)]
                            return old_key, new_key
                        else:
                            print("Error receiving keys")
                            return self.get_keys()
                    else:
                        print("Access not authorized")
                        return 'false', 'false'

reader = RFID()  # Instancia de la classe RFID per gestionar la comunicació RFID

# Funció per llegir les dades d'una targeta RFID
def readRfid(old_key, new_key):
    BLOCK_ADDRS, TRAILER = reader.define_block
