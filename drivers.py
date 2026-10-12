"""
Comprobación e instalación de los drivers que necesita el emulador.

- ViGEmBus: crea el mando de Xbox 360 virtual. Sin él no hay emulación.
- HidHide: oculta el DS4 real a los juegos. Opcional, pero evita que algunos
  juegos reciban cada pulsación dos veces.

El instalador de la app ya los instala, pero se pueden desinstalar después o
usar el .exe sin el instalador: por eso la app los comprueba y ofrece
instalarlos. Los instaladores de los drivers van en la carpeta "drivers" junto
al .exe (los copia el instalador de la app).
"""

import ctypes
import sys
import winreg
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path

# Opciones de los instaladores de Nefarius (Advanced Installer) para que
# instalen sin ventanas y sin reiniciar por su cuenta
OPCIONES_SILENCIOSO = "/exenoui /qn /norestart"


@dataclass(frozen=True)
class Driver:
    nombre: str
    servicio: str      # clave en HKLM\SYSTEM\CurrentControlSet\Services
    instalador: str    # nombre del archivo en la carpeta "drivers"
    descripcion: str
    web: str
    necesario: bool


VIGEMBUS = Driver(
    "ViGEmBus", "ViGEmBus", "ViGEmBus_Setup.exe",
    "Crea el mando de Xbox 360 virtual. Sin él, el emulador no funciona.",
    "https://github.com/nefarius/ViGEmBus/releases", True,
)
HIDHIDE = Driver(
    "HidHide", "HidHide", "HidHide_Setup.exe",
    "Oculta el DS4 real a los juegos para que no reciban cada pulsación dos veces.",
    "https://github.com/nefarius/HidHide/releases", False,
)
DRIVERS = (VIGEMBUS, HIDHIDE)


def instalado(driver):
    try:
        winreg.CloseKey(winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, rf"SYSTEM\CurrentControlSet\Services\{driver.servicio}"))
        return True
    except OSError:
        return False


def faltan():
    return [d for d in DRIVERS if not instalado(d)]


def carpeta_instaladores():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "drivers"
    return Path(__file__).parent / "instalador" / "redist"  # desde el código


def ruta_instalador(driver):
    ruta = carpeta_instaladores() / driver.instalador
    return ruta if ruta.exists() else None


# --- ejecutar como administrador -------------------------------------------

class _SHELLEXECUTEINFOW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIconOrMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]


SEE_MASK_NOCLOSEPROCESS = 0x40
SW_HIDE = 0
INFINITE = 0xFFFFFFFF
ERROR_CANCELLED = 1223  # el usuario dijo "No" en la ventana de permisos

_shell32 = ctypes.WinDLL("shell32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_shell32.ShellExecuteExW.argtypes = [ctypes.POINTER(_SHELLEXECUTEINFOW)]
_shell32.ShellExecuteExW.restype = wintypes.BOOL
_kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def comando_instalacion(drivers):
    """
    Línea para cmd.exe que instala los drivers uno detrás de otro. Así se
    pide permiso de administrador una sola vez para todos.
    """
    partes = [f'"{ruta_instalador(d)}" {OPCIONES_SILENCIOSO}' for d in drivers]
    # /s: cmd quita solo las comillas de los extremos y respeta las de dentro
    return f'/s /c "{" & ".join(partes)}"'


def instalar(drivers):
    """
    Instala los drivers indicados (con un solo aviso de permisos de Windows)
    y espera a que terminen. Tarda un rato: llamarlo fuera del hilo de la
    interfaz. Devuelve False si el usuario rechaza el permiso.
    """
    info = _SHELLEXECUTEINFOW()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = SEE_MASK_NOCLOSEPROCESS
    info.lpVerb = "runas"  # "ejecutar como administrador"
    info.lpFile = "cmd.exe"
    info.lpParameters = comando_instalacion(drivers)
    info.nShow = SW_HIDE
    if not _shell32.ShellExecuteExW(ctypes.byref(info)):
        error = ctypes.get_last_error()
        if error == ERROR_CANCELLED:
            return False
        raise ctypes.WinError(error)
    _kernel32.WaitForSingleObject(info.hProcess, INFINITE)
    _kernel32.CloseHandle(info.hProcess)
    return True
