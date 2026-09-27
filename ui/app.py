"""
app.py
------
Interfaz gráfica (Tkinter). Solo se encarga de mostrar ventanas,
botones y mensajes. Toda la lógica de cifrado real vive en
scripts/crypto_utils.py — esta ventana solo la llama.

Tkinter viene incluido con Python tanto en Windows como en Linux,
así que no hay que instalar nada aparte para la interfaz.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# Permite importar scripts/crypto_utils.py aunque este archivo
# esté dentro de la carpeta ui/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import crypto_utils


CARPETAS_INICIALES = {
    "Windows": "C:\\Users",
    "Linux": os.path.expanduser("~"),
    "Mac": os.path.expanduser("~"),
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Programa Encriptar - Cifrado de archivos")
        self.geometry("480x420")

        self.ruta_archivo = None  # archivo que el usuario seleccionó

        # --- Variables de estado de los controles ---
        self.var_sistema = tk.StringVar(value="Linux")
        self.var_accion = tk.StringVar(value="encriptar")

        self._construir_widgets()

    def _construir_widgets(self):
        tk.Label(self, text="1. Selecciona tu sistema operativo:").pack(anchor="w", padx=10, pady=(10, 0))
        frame_sistema = tk.Frame(self)
        frame_sistema.pack(anchor="w", padx=20)
        tk.Radiobutton(frame_sistema, text="Windows", variable=self.var_sistema, value="Windows").pack(side="left")
        tk.Radiobutton(frame_sistema, text="Linux", variable=self.var_sistema, value="Linux").pack(side="left")
        tk.Radiobutton(frame_sistema, text="Mac", variable=self.var_sistema, value="Mac").pack(side="left")

        tk.Label(self, text="2. ¿Qué quieres hacer?").pack(anchor="w", padx=10, pady=(10, 0))
        frame_accion = tk.Frame(self)
        frame_accion.pack(anchor="w", padx=20)
        tk.Radiobutton(frame_accion, text="Encriptar archivo", variable=self.var_accion, value="encriptar").pack(side="left")
        tk.Radiobutton(frame_accion, text="Desencriptar archivo", variable=self.var_accion, value="desencriptar").pack(side="left")

        tk.Label(self, text="3. Selecciona el archivo:").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Button(self, text="Elegir archivo...", command=self._elegir_archivo).pack(anchor="w", padx=20)
        self.label_archivo = tk.Label(self, text="(ningún archivo seleccionado)", fg="gray")
        self.label_archivo.pack(anchor="w", padx=20)

        tk.Label(self, text="4. Contraseña:").pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_password = tk.Entry(self, show="*", width=40)
        self.entry_password.pack(anchor="w", padx=20)

        tk.Button(self, text="Ejecutar", command=self._ejecutar, width=20).pack(pady=15)

        tk.Label(self, text="Registro:").pack(anchor="w", padx=10)
        self.text_log = tk.Text(self, height=8, width=55, state="disabled")
        self.text_log.pack(padx=10, pady=(0, 10))

    def _log(self, mensaje: str):
        self.text_log.configure(state="normal")
        self.text_log.insert("end", mensaje + "\n")
        self.text_log.configure(state="disabled")
        self.text_log.see("end")

    def _elegir_archivo(self):
        inicial = CARPETAS_INICIALES.get(self.var_sistema.get(), os.path.expanduser("~"))
        if not os.path.isdir(inicial):
            inicial = os.path.expanduser("~")

        if self.var_accion.get() == "encriptar":
            filtros = [("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        else:
            filtros = [("Archivos cifrados", "*.cif"), ("Todos los archivos", "*.*")]

        ruta = filedialog.askopenfilename(initialdir=inicial, filetypes=filtros)
        if ruta:
            self.ruta_archivo = ruta
            self.label_archivo.configure(text=os.path.basename(ruta), fg="black")

    def _ejecutar(self):
        if not self.ruta_archivo:
            messagebox.showwarning("Falta archivo", "Primero selecciona un archivo.")
            return

        password = self.entry_password.get()
        if not password:
            messagebox.showwarning("Falta contraseña", "Escribe una contraseña.")
            return

        carpeta_salida = os.path.dirname(self.ruta_archivo)

        try:
            if self.var_accion.get() == "encriptar":
                ruta_salida = crypto_utils.encriptar_archivo(self.ruta_archivo, password, carpeta_salida)
                self._log(f"Archivo encriptado con éxito:\n{ruta_salida}")
            else:
                ruta_salida = crypto_utils.desencriptar_archivo(self.ruta_archivo, password, carpeta_salida)
                self._log(f"Archivo desencriptado con éxito:\n{ruta_salida}")

            messagebox.showinfo("Listo", "Operación completada. Revisa el registro.")

        except crypto_utils.CryptoError as e:
            self._log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self._log(f"ERROR inesperado: {e}")
            messagebox.showerror("Error inesperado", str(e))


def iniciar():
    app = App()
    app.mainloop()
