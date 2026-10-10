"""
Paso 2: mostrar el estado decodificado del DualShock 4 en tiempo real.

Ejecutar:  .venv\\Scripts\\python paso2_decodificar.py
Salir:     Ctrl+C
"""

import os

from ds4 import DS4

VERDE = "\033[92m"
GRIS = "\033[90m"
RESET = "\033[0m"
SUBIR_LINEAS = "\033[{}F"
BORRAR_LINEA = "\033[K"


def boton(nombre, pulsado):
    return f"{VERDE if pulsado else GRIS}{nombre}{RESET}"


def barra(valor, ancho=20):
    llenos = valor * ancho // 255
    return "█" * llenos + "·" * (ancho - llenos)


def pintar(e):
    lineas = [
        f"Stick izq: X={e.stick_izq.x:3d} Y={e.stick_izq.y:3d}   "
        f"Stick der: X={e.stick_der.x:3d} Y={e.stick_der.y:3d}",
        f"L2 [{barra(e.l2)}] {e.l2:3d}   R2 [{barra(e.r2)}] {e.r2:3d}",
        "Cruceta: " + " ".join([
            boton("↑", e.arriba), boton("→", e.derecha),
            boton("↓", e.abajo), boton("←", e.izquierda),
        ]),
        "Botones: " + " ".join([
            boton("✕", e.cruz), boton("○", e.circulo),
            boton("□", e.cuadrado), boton("△", e.triangulo),
            boton("L1", e.l1), boton("R1", e.r1),
            boton("L3", e.l3), boton("R3", e.r3),
        ]),
        "Otros:   " + " ".join([
            boton("Share", e.share), boton("Options", e.options),
            boton("PS", e.ps), boton("Touchpad", e.touchpad),
        ]),
        f"Batería: {e.bateria * 10 if e.bateria <= 10 else 100}%"
        + (" (cargando)" if e.cable else ""),
    ]
    print("\n".join(linea + BORRAR_LINEA for linea in lineas))
    return len(lineas)


def main():
    os.system("")  # activa los códigos de color ANSI en consolas antiguas de Windows

    with DS4() as mando:
        print(f"Conectado: {mando.nombre}\n")
        lineas_pintadas = 0
        try:
            while True:
                estado = mando.leer()
                if estado is None:
                    continue
                if lineas_pintadas:
                    print(SUBIR_LINEAS.format(lineas_pintadas), end="")
                lineas_pintadas = pintar(estado)
        except KeyboardInterrupt:
            print("\nSaliendo.")


if __name__ == "__main__":
    main()
