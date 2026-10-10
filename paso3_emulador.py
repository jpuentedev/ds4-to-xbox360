"""
Paso 3: el DS4 se ve en Windows como un mando de Xbox 360.

Ejecutar:  .venv\\Scripts\\python paso3_emulador.py
Comprobar: Win+R → joy.cpl  (debe aparecer "Controller (XBOX 360 For Windows)")
Salir:     Ctrl+C
"""

import time

from ds4 import DS4
from xbox import Xbox360Virtual


def main():
    with DS4() as mando:
        xbox = Xbox360Virtual()
        print(f"{mando.nombre} → Xbox 360 virtual. Ctrl+C para salir.")

        reports = 0
        inicio = time.perf_counter()
        try:
            while True:
                estado = mando.leer()
                if estado is None:
                    continue
                xbox.enviar(estado)

                reports += 1
                transcurrido = time.perf_counter() - inicio
                if transcurrido >= 1:
                    print(f"\r{reports / transcurrido:.0f} reports/s", end="")
                    reports = 0
                    inicio = time.perf_counter()
        except KeyboardInterrupt:
            print("\nSaliendo.")


if __name__ == "__main__":
    main()
