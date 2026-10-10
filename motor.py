"""
Hilo de emulación: lee el DS4, alimenta el Xbox 360 virtual y avisa a la interfaz.

La interfaz nunca toca el mando directamente: cambia atributos del motor
(emular, modo_luz, color_fijo...) y el hilo los aplica en su siguiente vuelta.
"""

import time

from PySide6.QtCore import QThread, Signal

from ds4 import DS4
from xbox import Xbox360Virtual

MODO_LUZ_BATERIA = "bateria"
MODO_LUZ_FIJO = "fijo"

INTERVALO_REINTENTO = 1.0     # segundos entre intentos de encontrar el mando
TIMEOUT_DESCONEXION = 3.0     # sin datos durante este tiempo = mando apagado
INTERVALO_INTERFAZ = 1 / 60   # la vista se repinta como mucho a 60 Hz
REENVIO_SALIDA = 1.0
DURACION_PRUEBA_VIBRACION = 0.6
INTENSIDAD_PRUEBA_VIBRACION = 200


def color_bateria(nivel, cable):
    if cable:
        return (0, 0, 64)
    nivel = min(nivel, 10)
    return (int(255 * (10 - nivel) / 10), int(255 * nivel / 10), 0)


class Motor(QThread):
    conexion_cambiada = Signal(bool, str)  # conectado, nombre del mando
    emulacion_cambiada = Signal(bool)      # mando virtual creado / eliminado
    estado_actualizado = Signal(object)    # EstadoDS4
    luz_actualizada = Signal(tuple)        # color (r, g, b) enviado al mando
    tasa_actualizada = Signal(int)         # reports por segundo

    def __init__(self):
        super().__init__()
        self.emular = True
        self.modo_luz = MODO_LUZ_BATERIA
        self.color_fijo = (0, 0, 255)
        self._prueba_vibracion_hasta = 0.0
        self._detener = False

    def probar_vibracion(self):
        self._prueba_vibracion_hasta = time.perf_counter() + DURACION_PRUEBA_VIBRACION

    def detener(self):
        self._detener = True
        self.wait()

    def run(self):
        while not self._detener:
            try:
                mando = DS4()
            except (RuntimeError, OSError):
                self._esperar(INTERVALO_REINTENTO)
                continue

            self.conexion_cambiada.emit(True, mando.nombre)
            xbox = None
            try:
                xbox = self._bucle(mando)
            except OSError:
                pass  # el mando se ha desconectado a mitad de lectura
            finally:
                if xbox is not None:
                    xbox.cerrar()
                    self.emulacion_cambiada.emit(False)
                try:
                    mando.enviar_salida()  # parar vibración si sigue conectado
                except OSError:
                    pass
                mando.cerrar()
                self.conexion_cambiada.emit(False, "")

    def _esperar(self, segundos):
        fin = time.perf_counter() + segundos
        while not self._detener and time.perf_counter() < fin:
            self.msleep(50)

    def _bucle(self, mando):
        """Corre mientras el mando esté conectado. Devuelve el Xbox virtual si queda alguno abierto."""
        xbox = None
        ultima_lectura = time.perf_counter()
        ultima_salida = None
        ultimo_envio = 0.0
        ultimo_aviso_interfaz = 0.0
        reports = 0
        inicio_tasa = time.perf_counter()

        while not self._detener:
            estado = mando.leer(timeout_ms=200)
            ahora = time.perf_counter()
            if estado is None:
                if ahora - ultima_lectura > TIMEOUT_DESCONEXION:
                    return xbox
                continue
            ultima_lectura = ahora

            if self.emular and xbox is None:
                xbox = Xbox360Virtual()
                self.emulacion_cambiada.emit(True)
            elif not self.emular and xbox is not None:
                xbox.cerrar()
                xbox = None
                self.emulacion_cambiada.emit(False)

            if xbox is not None:
                xbox.enviar(estado)

            if ahora < self._prueba_vibracion_hasta:
                vibracion = (INTENSIDAD_PRUEBA_VIBRACION, INTENSIDAD_PRUEBA_VIBRACION)
            elif xbox is not None:
                vibracion = xbox.vibracion
            else:
                vibracion = (0, 0)

            if self.modo_luz == MODO_LUZ_FIJO:
                color = self.color_fijo
            else:
                color = color_bateria(estado.bateria, estado.cable)

            salida = (vibracion, color)
            if salida != ultima_salida or ahora - ultimo_envio >= REENVIO_SALIDA:
                mando.enviar_salida(vibracion[0], vibracion[1], color)
                if ultima_salida is None or color != ultima_salida[1]:
                    self.luz_actualizada.emit(color)
                ultima_salida = salida
                ultimo_envio = ahora

            if ahora - ultimo_aviso_interfaz >= INTERVALO_INTERFAZ:
                self.estado_actualizado.emit(estado)
                ultimo_aviso_interfaz = ahora

            reports += 1
            if ahora - inicio_tasa >= 1:
                self.tasa_actualizada.emit(round(reports / (ahora - inicio_tasa)))
                reports = 0
                inicio_tasa = ahora

        return xbox
