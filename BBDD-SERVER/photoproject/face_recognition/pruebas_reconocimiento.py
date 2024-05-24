#!/bin/env python3
from face_recognition import face_encodings, compare_faces, load_image_file  # Importa les funcions de reconeixement facial
import os  # Importa funcions del sistema operatiu

def troba_cares(imatge):
    """
    Troba les codificacions facials en la imatge proporcionada.
    :param imatge: Imatge carregada amb load_image_file.
    :return: Llista de codificacions facials.
    """
    codificacions = face_encodings(imatge)
    return codificacions

def compara_cares(directori_fotos, directori_bbdd):
    """
    Compara les cares a les imatges en el directori de fotos amb les del directori de la base de dades.
    :param directori_fotos: Directori que conté les fotos per comparar.
    :param directori_bbdd: Directori que conté la base de dades de cares conegudes.
    :return: El nom del directori trobat o None si no es troba coincidència.
    """
    nom_directori_trobat = None
    for subdir in os.listdir(directori_bbdd):  # Itera a través de tots els subdirectoris a la base de dades
        path_bbdd = os.path.join(directori_bbdd, subdir)
        if os.path.isdir(path_bbdd):  # Verifica si el camí és un directori
            for foto_photos in os.listdir(directori_fotos):  # Itera a través de totes les fotos al directori de fotos
                path_foto = os.path.join(directori_fotos, foto_photos)
                imatge_photos = load_image_file(path_foto)
                codificacio_photos = troba_cares(imatge_photos)
                if codificacio_photos:  # Si es troben codificacions facials a la foto
                    for foto_bbdd in os.listdir(path_bbdd):  # Itera a través de totes les fotos al directori de la base de dades
                        imatge_bbdd = load_image_file(os.path.join(path_bbdd, foto_bbdd))
                        codificacio_bbdd = troba_cares(imatge_bbdd)
                        if codificacio_bbdd:  # Si es troben codificacions facials a la foto de la base de dades
                            resultat = compare_faces(codificacio_bbdd, codificacio_photos[0])
                            if True in resultat:  # Si hi ha coincidència
                                nom_directori_trobat = subdir
                                break  # Sortim del bucle intern si trobem una coincidència
    return nom_directori_trobat

def eliminar_imatge(ruta_imatge):
    """
    Elimina la imatge especificada de la ruta proporcionada.
    :param ruta_imatge: Ruta completa de la imatge a eliminar.
    """
    try:
        os.remove(ruta_imatge)  # Intenta eliminar la imatge
    except OSError as e:  # Captura qualsevol error i el mostra
        print(f"Error en eliminar la imatge {ruta_imatge}: {e}")

def eliminar_totes_les_imatges(directori_fotos):
    """
    Elimina totes les imatges en el directori especificat.
    :param directori_fotos: Directori del qual eliminar totes les imatges.
    """
    for foto_fotos in os.listdir(directori_fotos):  # Itera a través de totes les fotos al directori
        path_foto = os.path.join(directori_fotos, foto_fotos)
        eliminar_imatge(path_foto)  # Crida a eliminar_imatge per a cada foto

def identificar_usuari(directori_fotos, directori_bbdd):
    """
    Intenta identificar l'usuari comparant les fotos al directori de fotos amb les fotos al directori de la base de dades.
    :param directori_fotos: Directori que conté les fotos per comparar.
    :param directori_bbdd: Directori que conté la base de dades de cares conegudes.
    :return: Resultat de la comparació.
    """
    try:
        nom_directori_trobat = compara_cares(directori_fotos, directori_bbdd)
        eliminar_totes_les_imatges(directori_fotos)  # Elimina totes les imatges després de la comparació
        return nom_directori_trobat
    except FileNotFoundError:  # Captura si un dels directoris no existeix
        print("Un dels directoris no ha estat trobat.")
        return False

if __name__ == "__main__":
    directori_fotos = r"/home/ubuntu/photoproject/photos"
    directori_bbdd = r"/home/ubuntu/bbddphotos/bbdd-directory"
    print(identificar_usuari(directori_fotos, directori_bbdd))