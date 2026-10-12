"""
Mando de Xbox 360 virtual (vía ViGEmBus + vgamepad) y traducción desde el DS4.
"""

import zona_muerta

# Botón del DS4 (nombre del campo en EstadoDS4) → botón de Xbox 360 (en vgamepad.XUSB_BUTTON)
MAPEO_BOTONES = {
    "cruz": "XUSB_GAMEPAD_A",
    "circulo": "XUSB_GAMEPAD_B",
    "cuadrado": "XUSB_GAMEPAD_X",
    "triangulo": "XUSB_GAMEPAD_Y",
    "l1": "XUSB_GAMEPAD_LEFT_SHOULDER",
    "r1": "XUSB_GAMEPAD_RIGHT_SHOULDER",
    "l3": "XUSB_GAMEPAD_LEFT_THUMB",
    "r3": "XUSB_GAMEPAD_RIGHT_THUMB",
    "share": "XUSB_GAMEPAD_BACK",
    "options": "XUSB_GAMEPAD_START",
    "ps": "XUSB_GAMEPAD_GUIDE",
    "arriba": "XUSB_GAMEPAD_DPAD_UP",
    "derecha": "XUSB_GAMEPAD_DPAD_RIGHT",
    "abajo": "XUSB_GAMEPAD_DPAD_DOWN",
    "izquierda": "XUSB_GAMEPAD_DPAD_LEFT",
}


def eje(valor):
    """-1.0 a 1.0 → Xbox (-32767 a 32767)."""
    return round(valor * 32767)


class Xbox360Virtual:
    def __init__(self):
        # vgamepad se conecta a ViGEmBus al importarse y, si el driver no está
        # instalado, lanza una excepción. Importarlo aquí y no arriba permite
        # que la app arranque igualmente y ofrezca instalarlo.
        import vgamepad as vg

        self._mando = vg.VX360Gamepad()
        self._botones = {campo: getattr(vg.XUSB_BUTTON, nombre) for campo, nombre in MAPEO_BOTONES.items()}
        # Último valor de vibración pedido por el juego: (fuerte, ligero), 0-255
        self.vibracion = (0, 0)
        self._mando.register_notification(callback_function=self._al_recibir_notificacion)

    def _al_recibir_notificacion(self, client, target, large_motor, small_motor, led_number, user_data):
        # Lo llama ViGEmBus desde otro hilo. Solo guardamos el valor; el bucle
        # principal es quien habla con el DS4, así evitamos usarlo desde dos hilos.
        self.vibracion = (large_motor, small_motor)

    def cerrar(self):
        """Desconecta el mando virtual de Windows."""
        if self._mando is None:
            return
        self._mando.unregister_notification()
        # vgamepad solo quita el mando de ViGEmBus cuando el objeto se destruye
        self._mando = None
        self.vibracion = (0, 0)

    def enviar(self, estado, zona_izq=0.0, zona_der=0.0):
        """Copia el EstadoDS4 al mando virtual, con la zona muerta de cada stick."""
        for campo, boton in self._botones.items():
            if getattr(estado, campo):
                self._mando.press_button(boton)
            else:
                self._mando.release_button(boton)

        # En el DS4 arriba es y negativa y en Xbox positiva: de ahí el -y
        x, y = zona_muerta.aplicar(estado.stick_izq, zona_izq)
        self._mando.left_joystick(eje(x), eje(-y))
        x, y = zona_muerta.aplicar(estado.stick_der, zona_der)
        self._mando.right_joystick(eje(x), eje(-y))
        self._mando.left_trigger(estado.l2)
        self._mando.right_trigger(estado.r2)

        self._mando.update()
