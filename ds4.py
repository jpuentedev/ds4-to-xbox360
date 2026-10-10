"""
Lectura y decodificación del DualShock 4.

Formato del report de entrada (por Bluetooth, report 0x11). Por USB es el
mismo contenido pero empieza 2 bytes antes (no lleva la cabecera BT).

  Byte  Contenido
  0     ID del report (0x11)
  1-2   Cabecera Bluetooth
  3     Stick izquierdo X   (0 = izquierda, 255 = derecha)
  4     Stick izquierdo Y   (0 = arriba,    255 = abajo)
  5     Stick derecho X
  6     Stick derecho Y
  7     bits 0-3: cruceta (0=N, 1=NE, 2=E ... 7=NO, 8=suelta)
        bit 4: □   bit 5: ✕   bit 6: ○   bit 7: △
  8     bit 0: L1  bit 1: R1  bit 2: L2  bit 3: R2
        bit 4: Share  bit 5: Options  bit 6: L3  bit 7: R3
  9     bit 0: PS  bit 1: clic touchpad  bits 2-7: contador
  10    Gatillo L2 analógico (0-255)
  11    Gatillo R2 analógico (0-255)
  32    bits 0-3: batería (0-10, hasta 11 cargando)  bit 4: cable conectado

Formato del report de salida (por Bluetooth, report 0x11, 78 bytes):

  Byte  Contenido
  0     ID del report (0x11)
  1     0xC0 | tasa de envío (0 = la más rápida, ~700 Hz; 4 ≈ 140 Hz)
  2     0x20
  3     Qué actualizar: 0x01 vibración, 0x02 barra de luz, 0x04 parpadeo
  4     0x04
  6     Motor derecho (ligero, 0-255)
  7     Motor izquierdo (fuerte, 0-255)
  8-10  Barra de luz R, G, B
  11-12 Parpadeo: tiempo encendido / apagado
  74-77 CRC32 (little endian) de 0xA2 + bytes 0-73
"""

import zlib
from dataclasses import dataclass, field

import hid

SONY_VID = 0x054C
DS4_PIDS = {
    0x05C4: "DualShock 4 v1",
    0x09CC: "DualShock 4 v2",
    0x0BA0: "Adaptador inalámbrico DS4",
}

REPORT_EXTENDIDO_BT = 0x11
FEATURE_CALIBRACION = 0x02
TAM_LECTURA = 78
BUS_BLUETOOTH = 2

TAM_SALIDA_BT = 78
TASA_MAXIMA = 0
ACTUALIZAR_VIBRACION = 0x01
ACTUALIZAR_LUZ = 0x02
# El CRC por Bluetooth incluye un byte de cabecera HID (0xA2 = "salida") que no
# se envía, pero el mando lo cuenta al verificar
CABECERA_CRC_SALIDA = 0xA2

# Desplazamiento donde empiezan los datos de los sticks en el report 0x11
BASE_BT = 3

# Índice = valor de la cruceta → (arriba, derecha, abajo, izquierda)
CRUCETA = [
    (True, False, False, False),   # 0 N
    (True, True, False, False),    # 1 NE
    (False, True, False, False),   # 2 E
    (False, True, True, False),    # 3 SE
    (False, False, True, False),   # 4 S
    (False, False, True, True),    # 5 SO
    (False, False, False, True),   # 6 O
    (True, False, False, True),    # 7 NO
    (False, False, False, False),  # 8 suelta
]


@dataclass
class Stick:
    x: int = 128
    y: int = 128


@dataclass
class EstadoDS4:
    stick_izq: Stick = field(default_factory=Stick)
    stick_der: Stick = field(default_factory=Stick)

    arriba: bool = False
    derecha: bool = False
    abajo: bool = False
    izquierda: bool = False

    cuadrado: bool = False
    cruz: bool = False
    circulo: bool = False
    triangulo: bool = False

    l1: bool = False
    r1: bool = False
    l3: bool = False
    r3: bool = False
    share: bool = False
    options: bool = False
    ps: bool = False
    touchpad: bool = False

    l2: int = 0  # 0-255
    r2: int = 0  # 0-255

    bateria: int = 0  # 0-10 (11 = cargada con cable)
    cable: bool = False


def bit(byte, n):
    return bool(byte & (1 << n))


def decodificar(datos):
    """Convierte un report 0x11 crudo en un EstadoDS4. Devuelve None si no lo es."""
    if len(datos) < 33 or datos[0] != REPORT_EXTENDIDO_BT:
        return None

    d = datos[BASE_BT:]
    e = EstadoDS4()

    e.stick_izq = Stick(d[0], d[1])
    e.stick_der = Stick(d[2], d[3])

    botones1 = d[4]
    cruceta = botones1 & 0x0F
    e.arriba, e.derecha, e.abajo, e.izquierda = CRUCETA[min(cruceta, 8)]
    e.cuadrado = bit(botones1, 4)
    e.cruz = bit(botones1, 5)
    e.circulo = bit(botones1, 6)
    e.triangulo = bit(botones1, 7)

    botones2 = d[5]
    e.l1 = bit(botones2, 0)
    e.r1 = bit(botones2, 1)
    e.share = bit(botones2, 4)
    e.options = bit(botones2, 5)
    e.l3 = bit(botones2, 6)
    e.r3 = bit(botones2, 7)

    botones3 = d[6]
    e.ps = bit(botones3, 0)
    e.touchpad = bit(botones3, 1)

    e.l2 = d[7]
    e.r2 = d[8]

    estado_bateria = d[29]
    e.bateria = estado_bateria & 0x0F
    e.cable = bit(estado_bateria, 4)

    return e


class DS4:
    """Conexión a un DualShock 4 por Bluetooth."""

    def __init__(self):
        info = next(
            (i for i in hid.enumerate(SONY_VID) if i["product_id"] in DS4_PIDS),
            None,
        )
        if info is None:
            raise RuntimeError("No se encontró ningún DualShock 4. ¿Está emparejado y encendido?")
        if info.get("bus_type") != BUS_BLUETOOTH:
            raise RuntimeError("De momento solo se soporta el DS4 por Bluetooth.")

        self.nombre = DS4_PIDS[info["product_id"]]
        self._dispositivo = hid.device()
        self._dispositivo.open_path(info["path"])
        # Pedir la calibración hace que el mando pase al report extendido 0x11
        self._dispositivo.get_feature_report(FEATURE_CALIBRACION, 37)

    def enviar_salida(self, motor_fuerte=0, motor_ligero=0, color=(0, 0, 32), tasa=TASA_MAXIMA):
        """Envía vibración y color de la barra de luz. También fija la tasa de envío."""
        salida = bytearray(TAM_SALIDA_BT)
        salida[0] = REPORT_EXTENDIDO_BT
        salida[1] = 0xC0 | tasa
        salida[2] = 0x20
        salida[3] = ACTUALIZAR_VIBRACION | ACTUALIZAR_LUZ
        salida[4] = 0x04
        salida[6] = motor_ligero
        salida[7] = motor_fuerte
        salida[8:11] = bytes(color)

        crc = zlib.crc32(bytes([CABECERA_CRC_SALIDA]) + salida[:74])
        salida[74:78] = crc.to_bytes(4, "little")
        self._dispositivo.write(bytes(salida))

    def leer(self, timeout_ms=1000):
        """Espera al siguiente report y lo devuelve decodificado (o None)."""
        datos = self._dispositivo.read(TAM_LECTURA, timeout_ms)
        return decodificar(datos) if datos else None

    def cerrar(self):
        self._dispositivo.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()
