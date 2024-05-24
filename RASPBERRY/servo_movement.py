import pigpio  # Importa la llibreria pigpio per controlar GPIO
from time import sleep  # Importa la funció sleep de la llibreria time

class ServoControl:
    def __init__(self, pi, pin=16):
        self.pi = pi  # Guarda la instància de pigpio
        self.pin = pin  # Guarda el pin assignat al servo
        self.pi.set_PWM_frequency(self.pin, 50)  # Configura la freqüència PWM a 50 Hz per servos
        self.pi.set_servo_pulsewidth(self.pin, 0)  # Estableix el servo en estat neutral

    def open_servo(self):
        self.pi.set_servo_pulsewidth(self.pin, 2500)  # Obre el servo
        print("Servo obert")

    def close_servo(self):
        self.pi.set_servo_pulsewidth(self.pin, 1500)  # Tanca el servo
        print("Servo tancat")

    def open_door(self):
        try:
            self.open_servo()  # Obre el servo
            sleep(10)  # Espera 10 segons
            self.close_servo()  # Tanca el servo després de 10 segons
            sleep(0.5)  # Espera 0.5 segons
        finally:
            self.close_servo()  # Assegura que el servo estigui tancat
            self.stop()  # Deté la instància del servo

    def stop(self):
        self.pi.set_servo_pulsewidth(self.pin, 0)  # Deté el servo
        self.pi.stop()  # Deté la connexió amb el daemon de pigpio

# Configuració inicial
pi = pigpio.pi()  # Inicialitza la connexió amb pigpio
instancia_servo = ServoControl(pi)  # Crea una instància de ServoControl

if __name__ == "__main__":
    try:
        while True:
            # Obre i tanca el servo en bucle
            instancia_servo.open_servo()  # Obre el servo
            print("Servo obert")
            sleep(0.6)  # Espera 0.6 segons
            instancia_servo.close_servo()  # Tanca el servo
            print("Servo tancat")
            sleep(0.6)  # Espera 0.6 segons
            input("Prem una tecla per continuar")  # Espera l'entrada de l'usuari per continuar
    except:
        instancia_servo.close_servo()  # Tanca el servo en cas d'excepció
        instancia_servo.stop()  # Deté la instància del servo en cas d'excepció

    finally:
        instancia_servo.close_servo()  # Tanca el servo al finalitzar
        instancia_servo.stop()  # Deté la instància del servo al finalitzar
