"""
Genera dist\\EmuladorDeControl\\EmuladorDeControl.exe con PyInstaller.

Ejecutar:  .venv\\Scripts\\python empaquetar.py

Necesita PyInstaller en el .venv (pip install pyinstaller). En el PC donde
se use el .exe tiene que estar instalado ViGEmBus (y HidHide si se quiere
ocultar el DS4): son drivers y no van dentro del .exe.
"""

import sys

import PyInstaller.__main__
from PySide6.QtWidgets import QApplication

NOMBRE = "EmuladorDeControl"
ICONO = "build/icono.ico"


def crear_icono_ico():
    """Guarda como .ico el mismo icono que la app dibuja por código."""
    from pathlib import Path

    from ventana import crear_icono

    Path(ICONO).parent.mkdir(exist_ok=True)
    _app = QApplication.instance() or QApplication(sys.argv)
    if not crear_icono().pixmap(64, 64).save(ICONO):
        raise RuntimeError(f"No se pudo guardar {ICONO}")


def main():
    crear_icono_ico()
    PyInstaller.__main__.run([
        "app.py",
        f"--name={NOMBRE}",
        f"--icon={ICONO}",
        "--windowed",       # sin ventana de consola
        "--onedir",         # carpeta con el .exe: arranca más rápido que --onefile
        "--noconfirm",      # sobrescribir la versión anterior sin preguntar
        "--clean",
        # vgamepad carga ViGEmClient.dll por su ruta: hay que llevarse la DLL
        "--collect-all=vgamepad",
    ])
    print(f"\nListo: dist\\{NOMBRE}\\{NOMBRE}.exe")


if __name__ == "__main__":
    main()
