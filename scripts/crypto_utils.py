"""
crypto_utils.py
----------------
Aquí vive TODA la lógica de cifrado/descifrado.
No sabe nada de ventanas ni botones: solo recibe rutas de archivo
y contraseñas, y devuelve resultados. Así la UI (ui/app.py) queda
separada del "motor" criptográfico.

Método usado: Fernet (de la librería `cryptography`).
- Fernet es cifrado simétrico basado en AES-128 en modo CBC + HMAC
  para verificar integridad (si alguien modifica el archivo cifrado,
  Fernet lo detecta y falla el descifrado en vez de dar datos corruptos).
- La llave de Fernet se deriva de la CONTRASEÑA del usuario usando
  PBKDF2HMAC, una función pensada para que adivinar la contraseña
  por fuerza bruta sea lento.

Formato del archivo cifrado que generamos (todo en binario):

    [4 bytes]  MAGIC           -> para identificar que es nuestro formato
    [16 bytes] SALT            -> usado por PBKDF2 para derivar la llave
    [4 bytes]  LEN_NOMBRE      -> longitud del nombre de archivo cifrado
    [N bytes]  NOMBRE_CIFRADO  -> nombre original del archivo, cifrado
    [resto]    CONTENIDO_CIFRADO -> contenido original del archivo, cifrado

Tanto el nombre como el contenido quedan cifrados, tal como pidió
el ejercicio.
"""

import os
import base64
import struct

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"CIF1"                 # firma de nuestro formato de archivo
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB, tope pedido en el ejercicio
SALT_SIZE = 16
KDF_ITERATIONS = 390_000        # número alto = más lento de "fuerza bruta"


class CryptoError(Exception):
    """Error propio para mostrar mensajes claros en la interfaz."""
    pass


def _derivar_llave(password: str, salt: bytes) -> bytes:
    """
    Convierte una contraseña (texto normal) + salt (bytes al azar)
    en una llave válida para Fernet (32 bytes, codificados en base64).

    El "salt" evita que dos personas con la misma contraseña generen
    la misma llave, y hace inútiles los ataques con tablas precalculadas.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    llave_cruda = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(llave_cruda)


def _validar_tamano(path: str):
    tamano = os.path.getsize(path)
    if tamano > MAX_FILE_SIZE:
        mb = tamano / (1024 * 1024)
        raise CryptoError(
            f"El archivo pesa {mb:.2f} MB. El máximo permitido es 20 MB."
        )


def encriptar_archivo(ruta_entrada: str, password: str, carpeta_salida: str) -> str:
    """
    Cifra un archivo (nombre + contenido) y guarda un archivo .cif
    en carpeta_salida. Devuelve la ruta del archivo generado.
    """
    _validar_tamano(ruta_entrada)

    with open(ruta_entrada, "rb") as f:  # 'rb' = leer como BYTES, no texto
        contenido = f.read()

    nombre_original = os.path.basename(ruta_entrada).encode("utf-8")

    salt = os.urandom(SALT_SIZE)
    llave = _derivar_llave(password, salt)
    fernet = Fernet(llave)

    nombre_cifrado = fernet.encrypt(nombre_original)
    contenido_cifrado = fernet.encrypt(contenido)

    nombre_salida = os.path.basename(ruta_entrada) + ".cif"
    ruta_salida = os.path.join(carpeta_salida, nombre_salida)

    with open(ruta_salida, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(struct.pack(">I", len(nombre_cifrado)))  # 4 bytes, longitud
        f.write(nombre_cifrado)
        f.write(contenido_cifrado)

    return ruta_salida


def desencriptar_archivo(ruta_entrada: str, password: str, carpeta_salida: str) -> str:
    """
    Descifra un archivo .cif generado por encriptar_archivo().
    Restaura el archivo con su nombre original en carpeta_salida.
    Devuelve la ruta del archivo restaurado.
    """
    _validar_tamano(ruta_entrada)

    with open(ruta_entrada, "rb") as f:
        datos = f.read()

    if datos[:4] != MAGIC:
        raise CryptoError("Este archivo no tiene el formato esperado (.cif).")

    salt = datos[4:4 + SALT_SIZE]
    resto = datos[4 + SALT_SIZE:]

    (len_nombre,) = struct.unpack(">I", resto[:4])
    resto = resto[4:]

    nombre_cifrado = resto[:len_nombre]
    contenido_cifrado = resto[len_nombre:]

    llave = _derivar_llave(password, salt)
    fernet = Fernet(llave)

    try:
        nombre_original = fernet.decrypt(nombre_cifrado).decode("utf-8")
        contenido_original = fernet.decrypt(contenido_cifrado)
    except InvalidToken:
        raise CryptoError(
            "No se pudo descifrar. La contraseña es incorrecta o el "
            "archivo fue modificado/corrompido."
        )

    ruta_salida = os.path.join(carpeta_salida, nombre_original)
    with open(ruta_salida, "wb") as f:
        f.write(contenido_original)

    return ruta_salida
