"""
Zona muerta de los sticks.

Los sticks nunca vuelven exactamente al centro (128): al soltarlos se quedan
en 126, 131... y con el desgaste aún más lejos. El juego lo toma como un
movimiento pequeño y la cámara o el personaje se mueven solos ("drift").

La zona muerta es un círculo alrededor del centro dentro del cual el stick
cuenta como suelto. Es radial (mide la distancia al centro, no cada eje por
separado) para no "pegar" el stick a los ejes al moverlo en diagonal.

Fuera del círculo se reescala: justo en el borde de la zona la salida empieza
en 0 y llega a 1 al fondo del recorrido. Sin esto habría un salto brusco de 0
al tamaño de la zona al salir de ella.
"""

import math


def normalizar(valor):
    """DS4 (0-255, centro 128) → -1.0 a 1.0, con el centro exacto en 0."""
    return max(-1.0, (valor - 128) / 127)


def aplicar(stick, zona):
    """
    Devuelve (x, y) entre -1.0 y 1.0 tras aplicar la zona muerta.

    stick: Stick del DS4 (x, y de 0 a 255; en y, arriba es 0).
    zona: radio de la zona muerta, de 0.0 (nada) a menos de 1.0.
    """
    x, y = normalizar(stick.x), normalizar(stick.y)
    distancia = math.hypot(x, y)
    if distancia <= zona:
        return 0.0, 0.0
    nueva = min((distancia - zona) / (1 - zona), 1.0)
    factor = nueva / distancia
    return x * factor, y * factor
