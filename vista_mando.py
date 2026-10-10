"""
Dibujo en vivo del DualShock 4.

Todo se dibuja en un lienzo lógico de ANCHO x ALTO y se escala al tamaño
del widget manteniendo la proporción.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget

ANCHO = 400
ALTO = 250

CUERPO = QColor("#2b2f36")
BORDE = QColor("#14161a")
BOTON = QColor("#40464f")
SIMBOLO = QColor("#9aa3ad")
ACTIVO = QColor("#4c9aff")
TEXTO = QColor("#e6e8eb")

COLORES_FRONTALES = {
    "triangulo": QColor("#3fd1a0"),
    "circulo": QColor("#ff5a6a"),
    "cruz": QColor("#6fa8ff"),
    "cuadrado": QColor("#f29be0"),
}


class VistaMando(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(ANCHO, ALTO)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._estado = None
        self._color_luz = QColor(0, 0, 0)
        self._conectado = False

    def set_estado(self, estado):
        self._estado = estado
        self.update()

    def set_color_luz(self, rgb):
        self._color_luz = QColor(*rgb)
        self.update()

    def set_conectado(self, conectado):
        self._conectado = conectado
        if not conectado:
            self._estado = None
        self.update()

    # --- dibujo -----------------------------------------------------------

    def paintEvent(self, _evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        escala = min(self.width() / ANCHO, self.height() / ALTO)
        p.translate((self.width() - ANCHO * escala) / 2, (self.height() - ALTO * escala) / 2)
        p.scale(escala, escala)

        if not self._conectado:
            p.setOpacity(0.35)

        e = self._estado
        self._gatillos(p, e)
        self._cuerpo(p)
        self._touchpad(p, e)
        self._cruceta(p, e)
        self._frontales(p, e)
        self._centrales(p, e)
        self._stick(p, QPointF(150, 158), e.stick_izq if e else None, e.l3 if e else False)
        self._stick(p, QPointF(250, 158), e.stick_der if e else None, e.r3 if e else False)

        if not self._conectado:
            p.setOpacity(1)
            p.setPen(TEXTO)
            p.setFont(QFont("Segoe UI", 13, QFont.Bold))
            p.drawText(QRectF(0, 0, ANCHO, ALTO), Qt.AlignCenter, "Buscando mando…")

    def _cuerpo(self, p):
        cuerpo = QPainterPath()
        cuerpo.addRoundedRect(QRectF(40, 48, 320, 112), 48, 48)
        # Empuñaduras: elipses inclinadas hacia fuera
        for cx, angulo in ((92, 18), (308, -18)):
            empunadura = QPainterPath()
            empunadura.addEllipse(QRectF(-38, -70, 76, 140))
            giro = QTransform().translate(cx, 170).rotate(angulo)
            cuerpo.addPath(giro.map(empunadura))
        p.setPen(QPen(BORDE, 2))
        p.setBrush(CUERPO)
        p.drawPath(cuerpo.simplified())

    def _gatillos(self, p, e):
        for x, gatillo, boton, texto in (
            (62, e.l2 if e else 0, e.l1 if e else False, "L"),
            (262, e.r2 if e else 0, e.r1 if e else False, "R"),
        ):
            # L2 / R2: medidor que se llena según cuánto se pulsa
            caja = QRectF(x, 4, 76, 22)
            p.setPen(QPen(BORDE, 1.5))
            p.setBrush(BOTON)
            p.drawRoundedRect(caja, 6, 6)
            if gatillo:
                lleno = QRectF(caja.left(), caja.top(), caja.width() * gatillo / 255, caja.height())
                p.setPen(Qt.NoPen)
                p.setBrush(ACTIVO)
                p.drawRoundedRect(lleno, 6, 6)
            p.setPen(TEXTO)
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.drawText(caja, Qt.AlignCenter, f"{texto}2  {gatillo}")

            # L1 / R1
            p.setPen(QPen(BORDE, 1.5))
            p.setBrush(ACTIVO if boton else BOTON)
            caja = QRectF(x, 30, 76, 14)
            p.drawRoundedRect(caja, 5, 5)
            p.setPen(TEXTO)
            p.drawText(caja, Qt.AlignCenter, f"{texto}1")

    def _touchpad(self, p, e):
        caja = QRectF(145, 56, 110, 62)
        p.setPen(QPen(BORDE, 1.5))
        p.setBrush(ACTIVO.darker(150) if e and e.touchpad else QColor("#24272d"))
        p.drawRoundedRect(caja, 8, 8)
        # Barra de luz en el borde superior, con el color real del mando
        p.setPen(Qt.NoPen)
        p.setBrush(self._color_luz)
        p.drawRoundedRect(QRectF(158, 50, 84, 4), 2, 2)

    def _cruceta(self, p, e):
        cx, cy, largo, grueso = 100, 100, 20, 17
        brazos = (
            (QRectF(cx - grueso / 2, cy - grueso / 2 - largo, grueso, largo), e.arriba if e else False),
            (QRectF(cx + grueso / 2, cy - grueso / 2, largo, grueso), e.derecha if e else False),
            (QRectF(cx - grueso / 2, cy + grueso / 2, grueso, largo), e.abajo if e else False),
            (QRectF(cx - grueso / 2 - largo, cy - grueso / 2, largo, grueso), e.izquierda if e else False),
        )
        p.setPen(QPen(BORDE, 1.5))
        p.setBrush(BOTON)
        p.drawRect(QRectF(cx - grueso / 2, cy - grueso / 2, grueso, grueso))
        for caja, pulsado in brazos:
            p.setBrush(ACTIVO if pulsado else BOTON)
            p.drawRoundedRect(caja, 3, 3)

    def _frontales(self, p, e):
        cx, cy, sep, radio = 300, 100, 25, 12
        botones = (
            ("triangulo", 0, -sep),
            ("circulo", sep, 0),
            ("cruz", 0, sep),
            ("cuadrado", -sep, 0),
        )
        for nombre, dx, dy in botones:
            centro = QPointF(cx + dx, cy + dy)
            pulsado = e is not None and getattr(e, nombre)
            color = COLORES_FRONTALES[nombre]
            p.setPen(QPen(BORDE, 1.5))
            p.setBrush(color if pulsado else BOTON)
            p.drawEllipse(centro, radio, radio)
            p.setPen(QPen(CUERPO if pulsado else color, 2))
            p.setBrush(Qt.NoBrush)
            self._simbolo(p, nombre, centro, 5.5)

    def _simbolo(self, p, nombre, c, r):
        if nombre == "triangulo":
            path = QPainterPath(QPointF(c.x(), c.y() - r))
            path.lineTo(c.x() + r, c.y() + r * 0.75)
            path.lineTo(c.x() - r, c.y() + r * 0.75)
            path.closeSubpath()
            p.drawPath(path)
        elif nombre == "circulo":
            p.drawEllipse(c, r, r)
        elif nombre == "cruz":
            p.drawLine(QPointF(c.x() - r, c.y() - r), QPointF(c.x() + r, c.y() + r))
            p.drawLine(QPointF(c.x() - r, c.y() + r), QPointF(c.x() + r, c.y() - r))
        else:
            p.drawRect(QRectF(c.x() - r * 0.8, c.y() - r * 0.8, r * 1.6, r * 1.6))

    def _centrales(self, p, e):
        p.setFont(QFont("Segoe UI", 6))
        for caja, pulsado, texto in (
            (QRectF(122, 58, 14, 24), e.share if e else False, "SHARE"),
            (QRectF(264, 58, 14, 24), e.options if e else False, "OPTIONS"),
        ):
            p.setPen(QPen(BORDE, 1.5))
            p.setBrush(ACTIVO if pulsado else BOTON)
            p.drawRoundedRect(caja, 5, 5)
            p.setPen(SIMBOLO)
            p.drawText(QRectF(caja.center().x() - 25, caja.top() - 12, 50, 10), Qt.AlignCenter, texto)

        p.setPen(QPen(BORDE, 1.5))
        p.setBrush(ACTIVO if e and e.ps else BOTON)
        p.drawEllipse(QPointF(200, 140), 10, 10)
        p.setPen(SIMBOLO)
        p.setFont(QFont("Segoe UI", 7, QFont.Bold))
        p.drawText(QRectF(190, 130, 20, 20), Qt.AlignCenter, "PS")

    def _stick(self, p, centro, stick, pulsado):
        radio_hueco, radio_seta = 28, 17
        p.setPen(QPen(BORDE, 2))
        p.setBrush(QColor("#1d2025"))
        p.drawEllipse(centro, radio_hueco, radio_hueco)

        x = y = 0.0
        if stick is not None:
            x = (stick.x - 128) / 128 * (radio_hueco - radio_seta)
            y = (stick.y - 128) / 128 * (radio_hueco - radio_seta)
        seta = QPointF(centro.x() + x, centro.y() + y)
        p.setPen(QPen(ACTIVO if pulsado else BORDE, 2.5))
        p.setBrush(BOTON.lighter(115))
        p.drawEllipse(seta, radio_seta, radio_seta)
