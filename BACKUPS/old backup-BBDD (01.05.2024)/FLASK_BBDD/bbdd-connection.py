#!/usr/bin/env python3
# Script de connexió amb la base de dades.
import mysql.connector

try:
    # Establir la connexió
    connexio = mysql.connector.connect(
        host="**",  # O la direcció IP del servidor de la base de dades si és remot
        user="**",
        password="**",
        database="**"
    )

    # Si la connexió s'ha establert amb èxit, imprimeix això
    print("Connexió establerta amb èxit.")

except mysql.connector.Error as e:
    print(f"Error en connectar-se a la base de dades: {e}")

finally:
    if (connexio.is_connected()):
        connexio.close()
        print("Connexió tancada.")
