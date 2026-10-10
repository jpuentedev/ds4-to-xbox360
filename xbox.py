"""
Mando de Xbox 360 virtual (vía ViGEmBus + vgamepad) y traducción desde el DS4.
"""

import vgamepad as vg

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
    """DS4 (0-255) → Xbox (-32768 a 32767)."""
    return valor * 257 - 32768


def eje_invertido(valor):
    """Igual que eje(), pero invertido: en el DS4 arriba es 0 y en Xbox es positivo."""
    return 32767 - valor * 257


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

    def enviar(self, estado):
        """Copia el EstadoDS4 al mando virtual."""
        for campo, boton in MAPEO_BOTONES.items():
            if getattr(estado, campo):
                self._mando.press_button(boton)
            else:
                self._mando.release_button(boton)

        self._mando.left_joystick(eje(estado.stick_izq.x), eje_invertido(estado.stick_izq.y))
        self._mando.right_joystick(eje(estado.stick_der.x), eje_invertido(estado.stick_der.y))
        self._mando.left_trigger(estado.l2)
        self._mando.right_trigger(estado.r2)

        self._mando.update()
