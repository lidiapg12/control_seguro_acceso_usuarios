-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    ID_Usuario INT AUTO_INCREMENT PRIMARY KEY,
    ID_Targeta BIGINT UNSIGNED UNIQUE,
    Nombre VARCHAR(15) NOT NULL,
    Apellido VARCHAR(15),
    Estado TINYINT NOT NULL DEFAULT 0,
    Fecha_Targeta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_estado CHECK (Estado IN (0, 1))
) AUTO_INCREMENT=1001;


-- Crear la tabla de claves targeta
CREATE TABLE claves_targeta (
    ID_usuari_Key INT NOT NULL,
    ID VARCHAR(13) NOT NULL,
    Clave INT(6) UNSIGNED ZEROFILL NOT NULL,
    PRIMARY KEY (ID_usuari_Key),
    FOREIGN KEY (ID_usuari_Key) REFERENCES usuarios(ID_Usuario)
);


-- Crear tabla accesos
CREATE TABLE accesos (
    ID_Usuario_Acceso INT,
    Puerta_1 TINYINT DEFAULT 0,
    Puerta_2 TINYINT DEFAULT 0,
    Puerta_3 TINYINT DEFAULT 0,
    Puerta_4 TINYINT DEFAULT 0,
    Puerta_5 TINYINT DEFAULT 0,
    PRIMARY KEY (ID_Usuario_Acceso),
    FOREIGN KEY (ID_Usuario_Acceso) REFERENCES usuarios(ID_Usuario)
);


CREATE TABLE logs (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    ID_Targeta_Log BIGINT UNSIGNED,
    Fecha_Hora_Acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Puerta INT,
    Acceso TINYINT,
    FOREIGN KEY (ID_Targeta_Log) REFERENCES usuarios(ID_Targeta)
);

CREATE VIEW vista_logs AS
    SELECT 
        l.Fecha_Hora_Acceso AS Fecha_Hora,
        u.ID_Targeta AS ID_Tarjeta,
        u.Nombre AS Nombre_Usuario,
        u.Apellido AS Apellido_Usuario,
        l.Puerta,
        l.Acceso
    FROM 
        logs l
    JOIN 
        usuarios u ON l.ID_Targeta_Log = u.ID_Targeta
    ORDER BY 
        l.Fecha_Hora_Acceso DESC;

describe logs;

INSERT INTO accesos (ID_Usuario_Acceso, Puerta_1, Puerta_2, Puerta_3, Puerta_4, Puerta_5)
VALUES
    (1003, 1, 0, 1, 0, 1),
    (1004, 1, 1, 0, 1, 0),
    (1005, 1, 1, 0, 1, 0),
    (1006, 0, 0, 1, 0, 1);

/*INSERTS PYTHON*/
/*
#!/bin/env python3
import random
import mysql.connector

# Datos de conexión a la base de datos
config = {
    'host': '',
    'user': '',
    'password': '',
    'database': ''
}

# Lista de nombres y apellidos de usuarios
usuarios = [
    {'nombre': 'Lidia', 'apellido': 'Panosa', 'estado': 1},
    {'nombre': 'Quim', 'apellido': 'Delgado', 'estado': 1},
    {'nombre': 'Hector', 'apellido': 'Escribano', 'estado': 1},
    {'nombre': 'Cristina', 'apellido': 'Fernandez', 'estado': 0}
]

def generar_id_targeta():
    return random.randint(100000000000, 999999999999)

def generar_clave():
    return random.randint(0, 999999)

def insertar_usuario(cursor, nombre, apellido, estado):
    id_targeta = generar_id_targeta()
    clave = generar_clave()
    query_usuario = "INSERT INTO usuarios (ID_Targeta, Nombre, Apellido, Estado) VALUES (%s, %s, %s, %s)"
    cursor.execute(query_usuario, (id_targeta, nombre, apellido, estado))
    id_usuario = cursor.lastrowid
    query_clave = "INSERT INTO claves_targeta (ID_Targeta_Key, Clave) VALUES (%s, %s)"
    cursor.execute(query_clave, (id_usuario, clave))

try:
    # Establecer conexión con la base de datos
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Insertar usuarios en la base de datos
    for usuario in usuarios:
        insertar_usuario(cursor, usuario['nombre'], usuario['apellido'], usuario['estado'])

    # Commit de los cambios
    conn.commit()
    print("Inserciones completadas con éxito.")

except mysql.connector.Error as err:
    print("Error de MySQL:", err)

finally:
    # Cerrar cursor y conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()

*/
