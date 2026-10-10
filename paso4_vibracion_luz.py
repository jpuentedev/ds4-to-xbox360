"""
Paso 4: emulador con vibración y barra de luz.

- La vibración que pide el juego al mando de Xbox se reenvía al DS4.
- La barra de luz indica la batería: verde (llena) → rojo (vacía).
- El DS4 pasa a enviar reports a la tasa máxima (~700 Hz).

Ejecutar:  .venv\\Scripts\\python paso4_vibracion_luz.py
Probar la vibración: https://hardwaretester.com/gamepad (botón "Test Vibration")
Salir:     Ctrl+C
"""

import time

from ds4 import DS4
from xbox import Xbox360Virtual

# Reenviamos la salida de vez en cuando aunque no cambie nada, por si el mando
# se ha perdido algún report
REENVIO_SEGUNDOS = 1.0


def color_bateria(nivel, cable):
    if cable:
        return (0, 0, 64)  # azul tenue mientras carga
    nivel = min(nivel, 10)
    return (int(255 * (10 - nivel) / 10), int(255 * nivel / 10), 0)


def main():
    with DS4() as mando:
        xbox = Xbox360Virtual()
        print(f"{mando.nombre} → Xbox 360 virtual (con vibración y luz). Ctrl+C para salir.")

        ultima_salida = None
        ultimo_envio = 0.0
        reports = 0
        inicio = time.perf_counter()
        try:
            while True:
                estado = mando.leer()
                if estado is None:
                    continue
                xbox.enviar(estado)

                salida = (xbox.vibracion, color_bateria(estado.bateria, estado.cable))
                ahora = time.perf_counter()
                if salida != ultima_salida or ahora - ultimo_envio >= REENVIO_SEGUNDOS:
                    (fuerte, ligero), color = salida
                    mando.enviar_salida(fuerte, ligero, color)
                    ultima_salida = salida
                    ultimo_envio = ahora

                reports += 1
                if ahora - inicio >= 1:
                    print(
                        f"\r{reports / (ahora - inicio):.0f} reports/s  "
                        f"vibración: {fuerte:3d}/{ligero:3d}  batería: {estado.bateria}",
                        end="",
                    )
                    reports = 0
                    inicio = ahora
        except KeyboardInterrupt:
            print("\nSaliendo.")
        finally:
            mando.enviar_salida()  # parar la vibración al salir


if __name__ == "__main__":
    main()
