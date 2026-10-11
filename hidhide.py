"""
Control de HidHide a través de su herramienta de línea de comandos.

HidHide es un filtro que oculta mandos a todos los programas salvo a los de
una lista blanca. Lo usamos para que los juegos solo vean el Xbox 360 virtual
y no también el DS4 real (si no, algunos juegos reciben cada pulsación dos
veces). El emulador tiene que estar en la lista blanca o dejaría de ver el DS4.

La CLI guarda la configuración en el driver, así que lo que se haga aquí
sigue activo aunque se cierre la app.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field

CLI = r"C:\Program Files\Nefarius Software Solutions\HidHide\x64\HidHideCLI.exe"
VENDOR_SONY = "054C"


@dataclass
class EstadoHidHide:
    instalado: bool = False
    activo: bool = False                                # ocultación encendida
    ds4_conectados: list = field(default_factory=list)  # rutas de los DS4 presentes
    ocultos: list = field(default_factory=list)         # rutas en la lista de ocultos
    apps: list = field(default_factory=list)            # lista blanca

    @property
    def emulador_permitido(self):
        apps = {a.lower() for a in self.apps}
        return all(p.lower() in apps for p in ejecutables_emulador())

    @property
    def ds4_oculto(self):
        ocultos = {o.lower() for o in self.ocultos}
        return self.activo and any(d.lower() in ocultos for d in self.ds4_conectados)


def instalado():
    return os.path.exists(CLI)


def ejecutables_emulador():
    """
    Ejecutables que deben poder ver el DS4.

    Con un .venv, Windows arranca primero .venv\\Scripts\\python.exe y este
    lanza el Python base, que es quien abre el mando: hacen falta los dos.
    """
    rutas = {sys.executable, getattr(sys, "_base_executable", sys.executable)}
    return sorted(r for r in rutas if os.path.exists(r))


def _ejecutar(*argumentos):
    resultado = subprocess.run(
        [CLI, *argumentos],
        stdin=subprocess.DEVNULL,  # si hereda la entrada de la app, puede quedarse esperando
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,  # sin ventana de consola
        timeout=10,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip() or f"HidHideCLI falló ({resultado.returncode})")
    return resultado.stdout


def _rutas(salida, opcion):
    """Extrae las rutas de líneas como: --app-reg "C:\\ruta"."""
    rutas = []
    for linea in salida.splitlines():
        linea = linea.strip()
        if linea.startswith(opcion):
            rutas.append(linea[len(opcion):].strip().strip('"'))
    return rutas


def _ds4_conectados():
    salida = _ejecutar("--dev-gaming").strip()
    if not salida:
        return []
    rutas = []
    for grupo in json.loads(salida):
        for d in grupo.get("devices", []):
            ruta = d.get("deviceInstancePath", "")
            if d.get("present") and VENDOR_SONY in ruta.upper():
                rutas.append(ruta)
    return rutas


def leer_estado():
    if not instalado():
        return EstadoHidHide()
    return EstadoHidHide(
        instalado=True,
        activo=_ejecutar("--cloak-state").strip() == "--cloak-on",
        ds4_conectados=_ds4_conectados(),
        ocultos=_rutas(_ejecutar("--dev-list"), "--dev-hide"),
        apps=_rutas(_ejecutar("--app-list"), "--app-reg"),
    )


def ocultar_ds4():
    """
    Pone el emulador en la lista blanca, oculta los DS4 conectados y activa
    la ocultación. Primero la lista blanca: si no, el emulador perdería el mando.
    Devuelve cuántos DS4 se han ocultado.
    """
    ds4 = _ds4_conectados()
    argumentos = []
    for ruta in ejecutables_emulador():
        argumentos += ["--app-reg", ruta]
    for ruta in ds4:
        argumentos += ["--dev-hide", ruta]
    argumentos.append("--cloak-on")
    _ejecutar(*argumentos)  # la CLI admite varios comandos seguidos
    return len(ds4)


def dejar_de_ocultar():
    """Apaga la ocultación (las listas se conservan para la próxima vez)."""
    _ejecutar("--cloak-off")
