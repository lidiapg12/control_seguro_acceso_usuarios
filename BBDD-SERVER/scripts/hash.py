from werkzeug.security import generate_password_hash  # Importa la funció per generar el hash de la contrasenya

# Defineix els noms d'usuari i contrasenyes
usuaris = {
    'cristina': 'iloveyou'  # Defineix un diccionari amb el nom d'usuari com a clau i la contrasenya com a valor
}

# Genera i imprimeix els hashes de contrasenyes
for usuari, contrasenya in usuaris.items():  # Itera a través de cada usuari i contrasenya al diccionari
    hash_contrasenya = generate_password_hash(contrasenya)  # Genera el hash de la contrasenya
    print(f"Usuari: {usuari}, Hash: {hash_contrasenya}")  # Imprimeix el nom de l'usuari i el seu hash de contrasenya
