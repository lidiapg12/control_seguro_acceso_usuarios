#!/bin/bash

# Actualitza el sistema i els paquets
sudo apt-get update && sudo apt-get upgrade -y

# Configuració perquè els canvis es facin sense interacció manual
# Habilita la comunicació I2C i SPI sense demanar confirmació
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Instal·la eines i llibreries necessàries per al projecte
sudo apt-get install -y python3 python3-pip i2c-tools

# Habilita el suport per a I2C en el sistema
sudo apt-get install -y python3-smbus
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
echo "i2c-dev" | sudo tee -a /etc/modules

# Instal·la les biblioteques de Python necessàries per al projecte
pip3 install RPi.GPIO spidev mfrc522 Pillow adafruit-circuitpython-ssd1306 flask gunicorn

# Reinicia el Raspberry Pi per aplicar els canvis
echo "Configuració completada, reiniciant en 10 segons..."
sleep 10
sudo reboot
