"""
Mando de Xbox 360 virtual (vía ViGEmBus + vgamepad) y traducción desde el DS4.
"""

import vgamepad as vg

import zona_muerta

B = vg.XUSB_BUTTON

# Botón del DS4 (nombre del campo en EstadoDS4) → botón de Xbox 360
MAPEO_BOTONES = {
    "cruz": B.XUSB_GAMEPAD_A,
    "circulo": B.XUSB_GAMEPAD_B,
    "cuadrado": B.XUSB_GAMEPAD_X,
    "triangulo": B.XUSB_GAMEPAD_Y,
    "l1": B.XUSB_GAMEPAD_LEFT_SHOULDER,
    "r1": B.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "l3": B.XUSB_GAMEPAD_LEFT_THUMB,
    "r3": B.XUSB_GAMEPAD_RIGHT_THUMB,
    "share": B.XUSB_GAMEPAD_BACK,
    "options": B.XUSB_GAMEPAD_START,
    "ps": B.XUSB_GAMEPAD_GUIDE,
    "arriba": B.XUSB_GAMEPAD_DPAD_UP,
    "derecha": B.XUSB_GAMEPAD_DPAD_RIGHT,
    "abajo": B.XUSB_GAMEPAD_DPAD_DOWN,
    "izquierda": B.XUSB_GAMEPAD_DPAD_LEFT,
}


def eje(valor):
    """-1.0 a 1.0 → Xbox (-32767 a 32767)."""
    return round(valor * 32767)


class Xbox360Virtual:
    def __init__(self):
        self._mando = vg.VX360Gamepad()
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
        for campo, boton in MAPEO_BOTONES.items():
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
