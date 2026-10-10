"""
Emulador de Control: DualShock 4 → Xbox 360.

Ejecutar:  .venv\Scripts\pythonw app.py   (sin consola)
       o:  .venv\Scripts\python app.py    (con consola, para ver errores)
"""

import sys

from PySide6.QtWidgets import QApplication

from tema import QSS
from ventana import VentanaPrincipal


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    # Que cerrar la ventana no cierre la app: sigue viva en la bandeja
    app.setQuitOnLastWindowClosed(False)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
