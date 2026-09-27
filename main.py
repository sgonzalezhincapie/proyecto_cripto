"""
main.py
-------
Punto de entrada. Ejecutar con:

    python main.py

Solo arranca la interfaz gráfica (ui/app.py).

NOTA sobre tkinter: tkinter viene incluido con Python, pero en
algunas instalaciones de Linux es un paquete aparte del sistema
operativo (no de pip), así que si falta, este archivo muestra el
comando exacto para instalarlo en lugar de un error críptico.
"""

import sys
import platform


def _mensaje_instalar_tkinter():
    sistema = platform.system()  # 'Linux', 'Windows' o 'Darwin' (Mac)

    print("No se encontró tkinter en tu instalación de Python.\n")

    if sistema == "Linux":
        print("Instálalo según tu distribución:")
        print("  Arch / Manjaro     -> sudo pacman -S tk")
        print("  Ubuntu / Debian    -> sudo apt install python3-tk")
        print("  Fedora             -> sudo dnf install python3-tkinter")
        print("  openSUSE           -> sudo zypper install python3-tk")
    elif sistema == "Darwin":
        print("En macOS instálalo con Homebrew:")
        print("  brew install python-tk")
        print("(o reinstala Python desde python.org, que ya lo incluye)")
    elif sistema == "Windows":
        print("En Windows, tkinter viene incluido con el instalador")
        print("oficial de python.org. Reinstala Python marcando la")
        print("casilla 'tcl/tk and IDLE' durante la instalación.")
    else:
        print("Instala tkinter según la documentación de tu sistema.")


try:
    from ui.app import iniciar
except ImportError:
    _mensaje_instalar_tkinter()
    sys.exit(1)


if __name__ == "__main__":
    iniciar()
