# Programa Encriptar

Programa con interfaz gráfica simple, hecho en Python, para
**encriptar y desencriptar archivos de texto**. Cifra el contenido
usando cifrado simétrico **AES** (a través de la librería
`cryptography`, específicamente su implementación `Fernet`). El
archivo cifrado conserva visible el nombre original seguido de
`.cif` (por ejemplo, `documento.txt.cif`), así que el nombre no queda
oculto.

Funciona igual en **Windows, Linux (cualquier distribución) y macOS**.

---

## Índice

- [Programa Encriptar](#programa-encriptar)
  - [Índice](#índice)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Cómo descargar el proyecto](#cómo-descargar-el-proyecto)
  - [Instalación](#instalación)
    - [tkinter (no se instala con pip)](#tkinter-no-se-instala-con-pip)
    - [Librería cryptography (sí se instala con pip)](#librería-cryptography-sí-se-instala-con-pip)
  - [Cómo usarlo](#cómo-usarlo)
  - [Flujo del programa](#flujo-del-programa)
  - [Conceptos de criptografía usados](#conceptos-de-criptografía-usados)
    - [AES (Advanced Encryption Standard)](#aes-advanced-encryption-standard)
    - [Salt (salado)](#salt-salado)
    - [PBKDF2 (derivación de la llave)](#pbkdf2-derivación-de-la-llave)
    - [Base64](#base64)
    - [HMAC (integridad)](#hmac-integridad)
  - [Explicación función por función](#explicación-función-por-función)
    - [`scripts/crypto_utils.py`](#scriptscrypto_utilspy)
    - [`ui/app.py`](#uiapppy)
    - [`main.py`](#mainpy)
  - [Formato del archivo .cif](#formato-del-archivo-cif)
  - [Límites y consideraciones](#límites-y-consideraciones)

---

## Estructura del proyecto

```
proyecto_cripto/
├── main.py                  <- Punto de entrada. Ejecutar este archivo.
├── requirements.txt         <- Dependencias instalables con pip.
├── README.md
├── ui/
│   ├── __init__.py
│   └── app.py                <- Toda la interfaz gráfica (Tkinter).
└── scripts/
    ├── __init__.py
    └── crypto_utils.py       <- Toda la lógica de cifrado/descifrado.
```

La idea de separar `ui/` de `scripts/` es que la ventana **no sabe
nada** de cómo funciona el cifrado por dentro; solo llama a
funciones como `encriptar_archivo(...)`. Si mañana queremos cambiar
la interfaz gráfica por una de consola, o cambiar Fernet por otro
algoritmo, solo tocamos una de las dos carpetas sin romper la otra.

---

## Cómo descargar el proyecto

El proyecto está en GitHub, clónalo con:

```bash
git clone https://github.com/saantigh/proyecto_cripto.git
cd proyecto_cripto
```

(o descarga el ZIP desde GitHub con el botón verde "Code" → "Download ZIP"
y descomprímelo).

---

## Instalación

El programa necesita dos cosas: **tkinter** (para la ventana) y la
librería **cryptography** (para el cifrado).

### tkinter (no se instala con pip)

`tkinter` viene incluido con Python, pero en Linux muchas
distribuciones lo separan como un paquete del sistema operativo, no
de Python. Por eso **no aparece en `requirements.txt`**: pip no
puede instalarlo correctamente, hay que instalarlo con el gestor de
paquetes del sistema operativo.

| Sistema operativo | Comando |
|---|---|
| Arch / Manjaro | `sudo pacman -S tk` |
| Ubuntu / Debian | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| openSUSE | `sudo zypper install python3-tk` |
| macOS (con Homebrew) | `brew install python-tk` |
| Windows | Ya viene incluido si instalaste Python desde python.org |

Si te falta, el programa te lo va a decir con el comando exacto al
ejecutarlo (no vas a ver un error críptico).

### Librería cryptography (sí se instala con pip)

Se recomienda usar un entorno virtual para no mezclar con otros
proyectos de Python:

```bash
python -m venv venv

# Activar el entorno virtual:
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows (cmd o PowerShell)

pip install -r requirements.txt
```

En Arch Linux, si no usas entorno virtual, es posible que pip te
pida la bandera `--break-system-packages`:

```bash
pip install -r requirements.txt --break-system-packages
```

---

## Cómo usarlo

```bash
python main.py
```

Se abre una ventana con 4 pasos:

1. **Selecciona tu sistema operativo** (Windows / Linux / Mac): esto
   solo cambia la carpeta que se abre por defecto al buscar el
   archivo (ej. `C:\Users` en Windows, tu carpeta personal en Linux
   o Mac).
2. **Elige la acción**: Encriptar o Desencriptar.
3. **Selecciona el archivo**:
   - Para encriptar: cualquier archivo `.txt`.
   - Para desencriptar: un archivo `.cif` generado por este mismo
     programa.
4. **Escribe una contraseña** (debe ser la misma al encriptar y al
   desencriptar el mismo archivo).
5. Click en **Ejecutar**. El resultado se guarda en la misma carpeta
   del archivo seleccionado, y aparece un registro en la ventana.

---

## Flujo del programa

Es importante entender que el programa **nunca modifica ni borra el
archivo que seleccionas**. Siempre crea un archivo nuevo:

**Al encriptar** `documento.txt`:
1. Se **abre y se lee** `documento.txt` (solo lectura).
2. Se crea `documento.txt.cif`; su nombre visible permite reconocer
  el archivo de origen. El formato también guarda una copia cifrada
  del nombre para restaurarlo al desencriptar, pero no lo oculta en
  el sistema de archivos.
3. Se **crea un archivo nuevo** llamado `documento.txt.cif` con el
  contenido cifrado.
4. `documento.txt` (el original) **queda intacto**, sin tocar.

**Al desencriptar** `documento.txt.cif`:
1. Se **abre y se lee** `documento.txt.cif` (solo lectura).
2. Se descifra el contenido y la copia interna del nombre usando la
  contraseña ingresada.
3. Se **crea un archivo nuevo** con el nombre original recuperado
   (`documento.txt`).
4. `documento.txt.cif` **queda intacto**, sin tocar.

Si la contraseña es incorrecta, o el archivo `.cif` fue modificado
por alguien, el programa **no genera datos corruptos**: detecta el
problema (gracias al HMAC de Fernet, ver más abajo) y muestra un
mensaje de error claro.

---

## Conceptos de criptografía usados

### AES (Advanced Encryption Standard)

Es el algoritmo de cifrado **simétrico** más usado del mundo (lo usan
bancos, WhatsApp, WiFi, etc.). "Simétrico" significa que se usa **la
misma llave** para cifrar y para descifrar (a diferencia del cifrado
asimétrico, que usa una llave pública y una privada distintas). AES
convierte el contenido original en un bloque de datos que parece
aleatorio, y solo alguien con la llave correcta puede revertir el
proceso.

En este proyecto no llamamos a AES directamente: lo usamos a través
de **Fernet**, que es una "receta" de la librería `cryptography` que
combina AES-128 en modo CBC (para cifrar) con HMAC-SHA256 (para
verificar que nadie alteró el archivo cifrado). Fernet es la forma
recomendada de usar AES de forma segura sin tener que configurar
manualmente modos de cifrado, vectores de inicialización, etc. (que
es donde más errores de seguridad cometen los desarrolladores).

### Salt (salado)

El "salt" es un valor aleatorio (en este proyecto, 16 bytes) que se
genera **cada vez** que encriptas un archivo, y se guarda sin cifrar
al inicio del archivo `.cif` resultante (no es secreto, no necesita
estar cifrado).

¿Para qué sirve? Si dos personas usan la misma contraseña
("123456", por ejemplo), sin salt generarían exactamente la misma
llave de cifrado. Con salt, cada archivo cifrado usa una llave
distinta aunque la contraseña sea igual, porque el salt es distinto
cada vez. Esto también hace inútiles los ataques con "tablas
precalculadas" (rainbow tables), donde un atacante ya tiene
calculadas las llaves para contraseñas comunes.

### PBKDF2 (derivación de la llave)

Fernet necesita una llave de 32 bytes, pero el usuario escribe una
contraseña de texto normal (ej. `"miClaveSegura123"`). **PBKDF2HMAC**
es la función que convierte contraseña + salt → llave de 32 bytes.

Lo interesante de PBKDF2 es que se puede configurar para que sea
**lento a propósito** (en este proyecto, 390.000 iteraciones
internas). Esto es intencional: si un atacante roba tu archivo `.cif`
y quiere adivinar la contraseña probando millones de combinaciones
(fuerza bruta), cada intento le toma más tiempo, lo que vuelve el
ataque mucho más costoso.

### Base64

AES produce **bytes binarios puros**, que pueden contener cualquier
valor (incluyendo bytes que no se pueden escribir como texto normal).
**Base64** es una forma de representar esos bytes usando solo 64
caracteres seguros (letras, números, `+`, `/`, `=`), para que se
puedan manejar como texto sin corromperse.

En este proyecto, Fernet internamente ya entrega sus resultados
codificados en base64 (por eso al ver un archivo `.cif` en un editor
de texto, la parte cifrada se ve como texto "raro" tipo
`gAAAAABquT0Ykc5iZAMQaLX8...` en vez de símbolos ilegibles). También
usamos base64 nosotros mismos en `_derivar_llave()`, porque Fernet
exige que la llave que le pasamos esté en ese formato.

### HMAC (integridad)

HMAC es como una "firma" que se calcula sobre los datos cifrados.
Fernet la agrega automáticamente. Sirve para detectar si el archivo
`.cif` fue modificado (por daño, o por un atacante) después de ser
cifrado: si la firma no coincide, Fernet se niega a descifrar y lanza
un error, en vez de devolver datos corruptos o manipulados sin
avisar.

---

## Explicación función por función

### `scripts/crypto_utils.py`

- **`_derivar_llave(password, salt)`**
  Convierte la contraseña (texto) + el salt (bytes aleatorios) en una
  llave de 32 bytes válida para Fernet, usando PBKDF2HMAC con SHA-256
  y 390.000 iteraciones. Devuelve la llave codificada en base64
  (formato que Fernet exige).

- **`_validar_tamano(path)`**
  Revisa el tamaño del archivo en disco con `os.path.getsize()`. Si
  supera los 20 MB, lanza `CryptoError` para frenar la operación
  antes de leer el archivo completo en memoria.

- **`encriptar_archivo(ruta_entrada, password, carpeta_salida)`**
  1. Valida el tamaño del archivo.
  2. Lee el archivo en modo binario (`"rb"`) para obtener sus bytes
     exactos, sin que Python intente interpretarlos como texto.
  3. Genera un salt aleatorio con `os.urandom(16)`.
  4. Deriva la llave y crea el objeto `Fernet`.
  5. Cifra el contenido y una copia interna del nombre, que se usa
     para restaurarlo al desencriptar. El nombre visible del `.cif`
     sigue siendo el original más la extensión `.cif`.
  6. Escribe un archivo `.cif` nuevo con: firma + salt + longitud del
     nombre cifrado + nombre cifrado + contenido cifrado.
  7. Devuelve la ruta del archivo `.cif` creado.

- **`desencriptar_archivo(ruta_entrada, password, carpeta_salida)`**
  1. Valida el tamaño del archivo `.cif`.
  2. Lee el archivo y verifica que empiece con la firma `CIF1`
     (si no, no es un archivo generado por este programa).
  3. Extrae el salt y la longitud del nombre cifrado.
  4. Separa el nombre cifrado del contenido cifrado usando esa
     longitud.
  5. Deriva la misma llave (con el mismo salt guardado en el
     archivo) y trata de descifrar ambas partes.
  6. Si la contraseña es incorrecta, Fernet lanza `InvalidToken`, que
     se convierte en un `CryptoError` con un mensaje claro.
  7. Si todo sale bien, escribe un archivo nuevo con el nombre y
     contenido originales, y devuelve su ruta.

### `ui/app.py`

- **`App.__init__`**: crea la ventana y sus variables de estado
  (sistema operativo elegido, acción elegida).
- **`_construir_widgets`**: arma todos los botones, radiobuttons,
  campo de contraseña y área de registro, sin ningún estilo extra
  (a propósito, para mantenerlo simple).
- **`_log(mensaje)`**: agrega una línea al cuadro de texto de
  registro, para que el usuario vea qué pasó.
- **`_elegir_archivo`**: abre el explorador de archivos nativo del
  sistema operativo (`filedialog.askopenfilename`), filtrando por
  `.txt` si vas a encriptar, o por `.cif` si vas a desencriptar.
- **`_ejecutar`**: valida que haya archivo y contraseña, luego llama
  a `crypto_utils.encriptar_archivo()` o
  `crypto_utils.desencriptar_archivo()` según corresponda, y muestra
  el resultado o el error.

### `main.py`

- **`_mensaje_instalar_tkinter()`**: si tkinter no está instalado,
  detecta el sistema operativo con `platform.system()` y muestra el
  comando exacto para instalarlo.
- Bloque `try/except`: intenta importar la interfaz; si falla por
  falta de tkinter, muestra el mensaje de ayuda en vez de un error
  críptico de Python.

---

## Formato del archivo .cif

Todo en binario, en este orden:

```
[4 bytes]  Firma "CIF1"          -> identifica el formato
[16 bytes] Salt                  -> usado por PBKDF2 para la llave
[4 bytes]  Longitud del nombre   -> cuántos bytes ocupa el nombre cifrado
[N bytes]  Nombre cifrado        -> nombre original del archivo, cifrado
[resto]    Contenido cifrado     -> contenido original, cifrado
```

Ni la firma ni el salt son secretos: son necesarios para poder
descifrar después, y no revelan nada sobre el contenido real del
archivo. Aunque el nombre almacenado dentro del formato está cifrado,
el nombre visible del archivo `.cif` no se oculta.

---

## Límites y consideraciones

- Tamaño máximo de archivo: **20 MB** (encriptar y desencriptar).
- Pensado por ahora para archivos de texto (`.txt`), aunque
  técnicamente cifra cualquier archivo porque siempre trabaja en
  modo binario.
- El archivo se lee y escribe siempre en modo **binario**
  (`"rb"` / `"wb"`), nunca en modo texto. Por eso el mismo código
  funciona igual con archivos `.txt` creados en Windows (saltos de
  línea `\r\n`) o en Linux/Mac (`\n`): los bytes se cifran tal cual,
  sin que Python intente "traducirlos".
- Si olvidas la contraseña, **no hay forma de recuperar el archivo**:
  así es como debe funcionar un cifrado real, no hay "puerta trasera".
