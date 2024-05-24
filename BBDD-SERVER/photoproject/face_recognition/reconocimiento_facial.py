#!/bin/env python3
# Importa les llibreries necessàries per al reconeixement facial i la manipulació de fitxers
from face_recognition import face_encodings, compare_faces, load_image_file  # Importa les funcions de reconeixement facial
import os  # Importa funcions del sistema operatiu

# Funció per trobar cares en una imatge
def troba_cares(imatge):
    """
    Retorna les codificacions facials trobades a la imatge proporcionada.
    :param imatge: Imatge carregada amb load_image_file.
    :return: Llista de codificacions facials.
    """
    codificacions = face_encodings(imatge)
    return codificacions

# Funció per comparar les cares de les imatges en un directori amb les de un altre directori
def compara_cares(directori_fotos, directori_bbdd):
    """
    Compara les cares de les imatges al directori de fotos amb les cares al directori de la base de dades.
    Elimina les imatges del directori de fotos després de la comparació, independentment del resultat.
    :param directori_fotos: Directori que conté les fotos a comparar.
    :param directori_bbdd: Directori que conté la base de dades de cares conegudes.
    :return: El subdirectori corresponent a la coincidència trobada, o False si no hi ha coincidències.
    """
    for subdir in os.listdir(directori_bbdd):  # Itera a través de cada subdirectori al directori de la base de dades
        path_bbdd = os.path.join(directori_bbdd, subdir)
        if os.path.isdir(path_bbdd):  # Verifica si el camí és un directori
            for foto_fotos in os.listdir(directori_fotos):  # Itera a través de cada foto al directori de fotos
                path_foto = os.path.join(directori_fotos, foto_fotos)
                imatge_fotos = load_image_file(path_foto)
                codificacio_fotos = troba_cares(imatge_fotos)
                if codificacio_fotos:  # Si es troben codificacions facials a la foto
                    for foto_bbdd in os.listdir(path_bbdd):  # Itera a través de cada foto al directori de la base de dades
                        imatge_bbdd = load_image_file(os.path.join(path_bbdd, foto_bbdd))
                        codificacio_bbdd = troba_cares(imatge_bbdd)
                        if codificacio_bbdd:  # Si es troben codificacions facials a la foto de la base de dades
                            resultat = compare_faces(codificacio_bbdd, codificacio_fotos[0])
                            if True in resultat:  # Si hi ha coincidència
                                eliminar_imatge(path_foto)  # Elimina la foto processada
                                return subdir  # Retorna el nom del subdirectori corresponent a la coincidència
    eliminar_totes_les_imatges(directori_fotos)  # Elimina totes les fotos restants si no es troben coincidències
    return False  # Retorna False si no hi ha coincidències

# Funció per eliminar una imatge especificada
def eliminar_imatge(ruta_imatge):
    """
    Elimina la imatge especificada de la ruta proporcionada.
    :param ruta_imatge: Ruta completa de la imatge a eliminar.
    """
    try:
        os.remove(ruta_imatge)  # Intenta eliminar la imatge
    except OSError as e:  # Captura qualsevol error i el mostra
        print(f"Error en eliminar la imatge {ruta_imatge}: {e}")

# Funció per eliminar totes les imatges en un directori
def eliminar_totes_les_imatges(directori_fotos):
    """
    Elimina totes les imatges al directori especificat.
    :param directori_fotos: Directori del qual eliminar totes les imatges.
    """
    for foto_fotos in os.listdir(directori_fotos):  # Itera a través de cada foto al directori
        path_foto = os.path.join(directori_fotos, foto_fotos)
        eliminar_imatge(path_foto)  # Crida a eliminar_imatge per a cada foto

# Funció principal per iniciar el procés de reconeixement facial
def identifica_usuari(directori_fotos, directori_bbdd):
    """
    Intenta identificar l'usuari comparant les fotos al directori de fotos amb les fotos al directori de la base de dades.
    :param directori_fotos: Directori que conté les fotos a comparar.
    :param directori_bbdd: Directori que conté la base de dades de cares conegudes.
    :return: Resultat de la comparació.
    """
    try:
        resultat = compara_cares(directori_fotos, directori_bbdd)  # Crida a compara_cares per a fer la comparació
        return resultat
    except FileNotFoundError:  # Captura si un dels directoris no existeix
        print("Un dels directoris no ha estat trobat.")
        return False

if __name__ == "__main__":
    # Defineix els directoris per a les fotos i la base de dades
    directori_fotos = r"/home/ubuntu/photoproject/photos"
    directori_bbdd = r"/home/ubuntu/bbddphotos/bbdd-directory"
    # Mostra el resultat de la identificació de l'usuari
    print(identifica_usuari(directori_fotos, directori_bbdd))
