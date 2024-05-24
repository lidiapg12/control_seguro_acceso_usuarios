#INSERT LOGIN V1
#!/bin/env python3
import hashlib
import mysql.connector

def hash_password(password):
    """Genera un hash SHA-512 de la contrasenya proporcionada."""
    sha512 = hashlib.sha512()
    sha512.update(password.encode('utf-8'))
    return sha512.hexdigest()

def main():
    # Sol·licitar a l'usuari que introdueixi el nom d'usuari
    usuari = input("Introdueix el nom d'usuari: ")
    # Sol·licitar a l'usuari que introdueixi la contrasenya
    contrasenya = input("Introdueix la contrasenya: ")

    # Fer hash de la contrasenya amb SHA-512
    contrasenya_hash = hash_password(contrasenya)

    # Mostrar el resultat
    print(f"Usuari: {usuari}")
    print(f"Hash de la contrasenya (SHA-512): {contrasenya_hash}")

    # Establir connexió amb la base de dades MySQL
    try:
        conn = mysql.connector.connect(
            host="**",
            user="**",
            password="**",
            database="**"
        )

        cursor = conn.cursor()

        # Inserir l'usuari i la contrasenya a la base de dades
        insert_query = "INSERT INTO login_web (usuari, password_hash) VALUES (%s, %s)"
        insert_values = (usuari, contrasenya_hash)
        cursor.execute(insert_query, insert_values)
        conn.commit()

        print("Usuari i contrasenya inserits correctament.")

    except mysql.connector.Error as err:
        print("Error en connectar amb la base de dades:", err)

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Connexió amb la base de dades tancada.")

if __name__ == "__main__":
    main()
