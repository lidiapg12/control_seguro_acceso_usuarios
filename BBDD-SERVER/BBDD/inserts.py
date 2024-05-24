#!/bin/env python3
# Importa les biblioteques necessàries
import random  # Importa la biblioteca random per generar nombres aleatoris
import mysql.connector  # Importa el connector MySQL per connectar amb la base de dades

# Configuració per connectar amb la base de dades
configuracio = {
    'host': '**',  # Adreça del servidor de la base de dades
    'usuari': '**',  # Nom d'usuari per connectar amb la base de dades
    'contrasenya': '**',  # Contrasenya per connectar amb la base de dades
    'base_dades': '**'  # Nom de la base de dades
}

# Llista de noms i cognoms dels usuaris amb el seu estat
usuaris = [
    {'nom': 'Lídia', 'cognom': 'Panosa', 'estat': 1},  # Usuari actiu
    {'nom': 'Quim', 'cognom': 'Delgado', 'estat': 1},  # Usuari actiu
    {'nom': 'Hèctor', 'cognom': 'Escribano', 'estat': 1},  # Usuari actiu
    {'nom': 'Cristina', 'cognom': 'Fernández', 'estat': 0}  # Usuari inactiu
]

# Funció per generar un ID de targeta aleatori
def generar_id_targeta():
    return random.randint(100000000000, 999999999999)  # Retorna un nombre aleatori de 12 dígits

# Funció per generar una clau aleatòria
def generar_clau():
    return random.randint(0, 999999)  # Retorna un nombre aleatori entre 0 i 999999

# Funció per inserir un usuari a la base de dades
def inserir_usuari(cursor, nom, cognom, estat):
    # Genera un ID de targeta i una clau aleatòria
    id_targeta = generar_id_targeta()
    clau = generar_clau()
    
    # Consulta SQL per inserir un usuari a la taula 'usuaris'
    consulta_usuari = "INSERT INTO usuaris (ID_Targeta, Nom, Cognom, Estat) VALUES (%s, %s, %s, %s)"
    # Executa la consulta amb els valors proporcionats
    cursor.execute(consulta_usuari, (id_targeta, nom, cognom, estat))
    # Obté l'ID de l'usuari inserit
    id_usuari = cursor.lastrowid
    
    # Consulta SQL per inserir una clau de targeta a la taula 'claus_targeta'
    consulta_clau = "INSERT INTO claus_targeta (ID_Targeta_Clau, Clau) VALUES (%s, %s)"
    # Executa la consulta amb els valors proporcionats
    cursor.execute(consulta_clau, (id_usuari, clau))

try:
    # Intenta connectar amb la base de dades
    connexio = mysql.connector.connect(**configuracio)
    # Obre un cursor per executar consultes
    cursor = connexio.cursor()

    # Insereix els usuaris a la base de dades
    for usuari in usuaris:
        inserir_usuari(cursor, usuari['nom'], usuari['cognom'], usuari['estat'])

    # Fa commit dels canvis a la base de dades
    connexio.commit()
    print("Insercions completades amb èxit.")  # Mostra un missatge d'èxit en pantalla

except mysql.connector.Error as err:
    print("Error de MySQL:", err)  # Mostra un missatge d'error si hi ha algun problema amb MySQL

finally:
    # Tanca el cursor i la connexió a la base de dades
    if 'cursor' in locals():
        cursor.close()
    if 'connexio' in locals():
        connexio.close()
