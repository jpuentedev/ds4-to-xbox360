"""
Genera dist\\EmuladorDeControl\\EmuladorDeControl.exe con PyInstaller y,
con --instalador, también dist\\EmuladorDeControl_Setup.exe con Inno Setup.

Ejecutar:  .venv\\Scripts\\python empaquetar.py               (solo la app)
           .venv\\Scripts\\python empaquetar.py --instalador  (app + instalador)

Necesita PyInstaller en el .venv (pip install -r requirements-dev.txt) y,
para el instalador, Inno Setup 6 (winget install --id JRSoftware.InnoSetup).
El instalador incluye ViGEmBus y HidHide: los descarga winget la primera vez
(verificando el hash) en instalador\\redist\\.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__
from PySide6.QtWidgets import QApplication

NOMBRE = "EmuladorDeControl"
VERSION = "1.1.0"
ICONO = "build/icono.ico"
REDIST = Path("instalador/redist")
# Paquete de winget → nombre con el que lo espera instalador.iss
DRIVERS = {
    "ViGEm.ViGEmBus": "ViGEmBus_Setup.exe",
    "Nefarius.HidHide": "HidHide_Setup.exe",
}
RUTAS_ISCC = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Inno Setup 6/ISCC.exe",
    Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
]


def crear_icono_ico():
    """Guarda como .ico el mismo icono que la app dibuja por código."""
    from ventana import crear_icono

    Path(ICONO).parent.mkdir(exist_ok=True)
    _app = QApplication.instance() or QApplication(sys.argv)
    if not crear_icono().pixmap(64, 64).save(ICONO):
        raise RuntimeError(f"No se pudo guardar {ICONO}")


def construir_app():
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


def descargar_drivers():
    """Baja con winget los instaladores que falten en instalador\\redist."""
    REDIST.mkdir(parents=True, exist_ok=True)
    for paquete, nombre in DRIVERS.items():
        destino = REDIST / nombre
        if destino.exists():
            continue
        temporal = REDIST / "descarga"
        subprocess.run(
            ["winget", "download", "--id", paquete, "-d", str(temporal),
             "--accept-package-agreements", "--accept-source-agreements"],
            check=True,
        )
        descargado = next(temporal.glob("*.exe"))
        descargado.replace(destino)
        shutil.rmtree(temporal)


def construir_instalador():
    iscc = next((r for r in RUTAS_ISCC if r.exists()), None)
    if iscc is None:
        sys.exit("No encuentro Inno Setup 6: winget install --id JRSoftware.InnoSetup")
    descargar_drivers()
    subprocess.run([str(iscc), f"/DVersion={VERSION}", "instalador/instalador.iss"], check=True)
    print(f"\nListo: dist\\{NOMBRE}_Setup.exe")


def main():
    construir_app()
    if "--instalador" in sys.argv:
        construir_instalador()


if __name__ == "__main__":
    main()
