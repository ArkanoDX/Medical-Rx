import sqlite3
import os
import hashlib
import binascii  # Lo usaremos para el 'salt' de las contraseñas

# --- 1. Configuración de Rutas (Paths) ---

# Esta es una forma robusta de encontrar la carpeta raíz del proyecto, sin importar desde dónde ejecutes el script.
# __file__ -> es este archivo (base_datos.py)
# os.path.dirname(__file__) -> la carpeta que lo contiene (model/)
# os.path.dirname(...) -> sube un nivel a la raíz (Medical_Rx/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Creamos la ruta a la carpeta 'data' y al archivo de la base de datos
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'consultorio.db')

# Nos aseguramos de que la carpeta 'data/' exista. Si no, la crea.
os.makedirs(DATA_DIR, exist_ok=True)


# --- 2. Funciones de Seguridad para Contraseñas ---

def hash_password(password):
    """
    Genera un hash seguro para la contraseña usando un 'salt' aleatorio.
    Nunca guardamos la contraseña original.
    """
    # Generamos un 'salt' (una cadena aleatoria) para esta contraseña específica
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

    # Generamos el hash usando PBKDF2 (un estándar de la industria)
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)

    # Guardamos el 'salt' y el 'hash' juntos. Los necesitaremos a ambos para verificar.
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password_hash, provided_password):
    """
    Verifica si la contraseña proporcionada (provided_password)
    coincide con la que está guardada (stored_password_hash).
    """
    # Extraemos el 'salt' y el 'hash' que guardamos juntos
    salt = stored_password_hash[:64].encode('ascii')
    stored_hash = stored_password_hash[64:]

    # Calculamos el hash de la contraseña proporcionada usando el MISMO 'salt'
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')

    # Comparamos si son idénticos
    return pwdhash == stored_hash


# --- 3. Creación de la Estructura de la Base de Datos ---

def crear_tablas():
    """
    Se conecta a la base de datos y crea las tres tablas
    principales si estas no existen.
    """
    conn = None
    try:
        # sqlite3.connect() crea el archivo .db si no existe
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Habilitar el soporte para llaves foráneas (FOREIGN KEYs)
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Tabla Doctores ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Doctores (
            id_doctor INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            cedula_profesional TEXT,
            especialidad TEXT,
            universidad TEXT,
            direccion_consultorio TEXT,
            telefono_consultorio TEXT,
            ruta_avatar TEXT
        )
        """)

        # --- Tabla Pacientes ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pacientes (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            fecha_nacimiento TEXT,
            telefono TEXT
        )
        """)

        # --- Tabla Consultas ---
        # Esta es la tabla que une todo
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Consultas (
            id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            diagnostico TEXT,
            medicamentos TEXT,
            indicaciones TEXT,
            id_doctor_fk INTEGER NOT NULL,
            id_paciente_fk INTEGER NOT NULL,
            FOREIGN KEY (id_doctor_fk) REFERENCES Doctores (id_doctor),
            FOREIGN KEY (id_paciente_fk) REFERENCES Pacientes (id_paciente)
        )
        """)

        # Guardamos los cambios en la base de datos
        conn.commit()
        print(f"Éxito: Base de datos y tablas creadas en '{DB_PATH}'")

    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")

    finally:
        # Nos aseguramos de cerrar la conexión
        if conn:
            conn.close()


# --- 4. Funciones de Gestión de Doctores ---

def registrar_doctor(usuario, contrasena, nombre_completo, cedula, especialidad, universidad, direccion, telefono):
    """
    Registra un nuevo doctor en la base de datos.
    Hashea la contraseña antes de guardarla.
    """
    # Hasheamos la contraseña
    contrasena_hash = hash_password(contrasena)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Preparamos la sentencia SQL para insertar el nuevo doctor
        # Usamos '?' como placeholders para prevenir inyección SQL
        cursor.execute("""
        INSERT INTO Doctores (usuario, contrasena_hash, nombre_completo, cedula_profesional, especialidad, universidad, direccion_consultorio, telefono_consultorio, ruta_avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (usuario, contrasena_hash, nombre_completo, cedula, especialidad, universidad, direccion, telefono, None))

        conn.commit()
        print(f"Éxito: Doctor '{usuario}' registrado.")
        return True

    except sqlite3.IntegrityError:
        # Esto ocurre si el 'usuario' ya existe (por la restricción UNIQUE)
        print(f"Error: El nombre de usuario '{usuario}' ya existe.")
        return False
    except sqlite3.Error as e:
        print(f"Error al registrar al doctor: {e}")
        return False
    finally:
        if conn:
            conn.close()


def validar_doctor(usuario, contrasena):
    """
    Valida las credenciales de un doctor.
    Devuelve los datos del doctor si es exitoso, o None si falla.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Usamos row_factory para que nos devuelva los resultados como un diccionario
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Buscamos al doctor por su nombre de usuario
        cursor.execute("SELECT * FROM Doctores WHERE usuario = ?", (usuario,))
        doctor_data = cursor.fetchone()  # fetchone() obtiene el primer (y único) resultado

        if doctor_data is None:
            # No se encontró el usuario
            print("Error: Usuario no encontrado.")
            return None

        # 2. Verificamos la contraseña
        stored_hash = doctor_data['contrasena_hash']
        if verify_password(stored_hash, contrasena):
            # ¡Contraseña correcta!
            print(f"Éxito: Inicio de sesión correcto para '{usuario}'.")
            # Devolvemos los datos del doctor (como un diccionario)
            return dict(doctor_data)
        else:
            # Contraseña incorrecta
            print("Error: Contraseña incorrecta.")
            return None

    except sqlite3.Error as e:
        print(f"Error al validar al doctor: {e}")
        return None
    finally:
        if conn:
            conn.close()


# --- 5. Bloque de Ejecución ---

if __name__ == "__main__":
    print("Iniciando configuración de la base de datos...")
    crear_tablas()

    # --- PRUEBA RÁPIDA (Opcional) ---
    # Vamos a registrar un doctor de prueba la primera vez que ejecutamos esto
    # Descomenta las siguientes líneas para registrar un usuario de prueba.
    # ¡Recuerda comentarlas de nuevo después de la primera ejecución!
    # ---
    # print("\nRegistrando doctor de prueba...")
    # registrar_doctor(
    #     "dr_prueba",
    #     "12345",
    #     "Dr. Juan Pérez",
    #     "12345678",
    #     "Cardiología",
    #     "UNAM",
    #     "Calle Falsa 123",
    #     "55-1234-5678"
    # )

    # --- Prueba de validación ---
    # Descomenta esto para probar el login
    # ---
    # print("\nValidando doctor...")
    # validar_doctor("dr_prueba", "12345") # Debería funcionar
    # print("\nProbando validación incorrecta...")
    # validar_doctor("dr_prueba", "contraseñamala") # Debería fallar