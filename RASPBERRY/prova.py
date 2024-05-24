import rfid  # Importa el mòdul rfid per llegir la targeta RFID
from camera import take_pic  # Importa la funció take_pic del mòdul camera per capturar una foto
from i2c import instancia_display as display, Bitmaps  # Importa el display i els bitmaps del mòdul i2c
from buzzer_sound import instancia_buzzer as buzzer  # Importa el buzzer del mòdul buzzer_sound
from servo_movement import instancia_servo as servo  # Importa el servo del mòdul servo_movement

try:
    display.draw_bitmap(Bitmaps.apropa_targeta)  # Mostra un bitmap per apropar la targeta
    print(rfid.readRfid())  # Llegeix la targeta RFID i imprimeix el resultat
    print(take_pic())  # Captura una foto i imprimeix el resultat

finally:
    display.clear_display()  # Esborra el contingut del display quan finalitza el programa
