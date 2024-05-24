#!/bin/bash

# Actualitzar el sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instal·lar pip i dependències de Python
sudo apt-get install -y python3-pip
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Instal·lar dependències per a dlib
sudo apt-get install -y cmake

# Instal·lar llibreries d'imatge
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev

# Instal·lar dependències d'OpenCV
sudo apt-get install -y libsm6 libxext6 libxrender-dev

# Instal·lar dlib (pot trigar una estona)
pip3 install dlib

# Instal·lar face_recognition
pip3 install face_recognition

# Instal·lar opencv-python
pip3 install opencv-python

echo "Instal·lació completada."

sleep 10
sudo poweroff
