"""
Dibujo en vivo del DualShock 4.

Todo se dibuja en un lienzo lógico de ANCHO x ALTO y se escala al tamaño
del widget manteniendo la proporción.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QTransform,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

ANCHO = 400
ALTO = 250

# Mando blanco con detalles negros ("Glacier White", ver diseñoGemini.md)
CUERPO = QColor("#FFFFFF")
CUERPO_SOMBRA = QColor("#E2E8F0")  # extremos del cuerpo, para dar volumen
BORDE = QColor("#CBD5E1")
PIEZA = QColor("#1F2937")  # cruceta, sticks, botones
GATILLO = QColor("#374151")
TOUCHPAD = QColor("#111827")
TOUCHPAD_RAYA = QColor("#1F2937")
ANILLO_STICK = QColor("#9CA3AF")
ACTIVO = QColor("#2563EB")
TEXTO = QColor("#1F2937")  # sobre el fondo claro de la app
TEXTO_PIEZA = QColor("#FFFFFF")  # sobre las piezas negras
ETIQUETA = QColor("#6B7280")  # SHARE / OPTIONS, sobre el cuerpo blanco

COLORES_FRONTALES = {
    "triangulo": QColor("#10B981"),
    "circulo": QColor("#EF4444"),
    "cruz": QColor("#3B82F6"),
    "cuadrado": QColor("#EC4899"),
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
        # WindingFill: las zonas donde se solapan las piezas se rellenan
        # (con el OddEvenFill por defecto quedarían huecos)
        cuerpo.setFillRule(Qt.WindingFill)
        cuerpo.addRoundedRect(QRectF(40, 48, 320, 112), 48, 48)
        # Empuñaduras: elipses inclinadas hacia fuera
        for cx, angulo in ((92, 18), (308, -18)):
            empunadura = QPainterPath()
            empunadura.addEllipse(QRectF(-38, -70, 76, 140))
            giro = QTransform().translate(cx, 170).rotate(angulo)
            cuerpo.addPath(giro.map(empunadura))

        # Blanco en el centro que se oscurece un poco hacia los lados
        degradado = QLinearGradient(40, 0, 360, 0)
        degradado.setColorAt(0, CUERPO_SOMBRA)
        degradado.setColorAt(0.25, CUERPO)
        degradado.setColorAt(0.75, CUERPO)
        degradado.setColorAt(1, CUERPO_SOMBRA)
        p.setPen(QPen(BORDE, 1.5))
        p.setBrush(degradado)
        p.drawPath(cuerpo.simplified())

    def _gatillos(self, p, e):
        for x, gatillo, boton, texto in (
            (62, e.l2 if e else 0, e.l1 if e else False, "L"),
            (262, e.r2 if e else 0, e.r1 if e else False, "R"),
        ):
            # L2 / R2: se rellena de abajo arriba según cuánto se pulsa
            caja = QRectF(x, 4, 76, 22)
            p.setPen(Qt.NoPen)
            p.setBrush(GATILLO)
            p.drawRoundedRect(caja, 6, 6)
            if gatillo:
                alto = caja.height() * gatillo / 255
                lleno = QRectF(caja.left(), caja.bottom() - alto, caja.width(), alto)
                p.save()
                recorte = QPainterPath()
                recorte.addRoundedRect(caja, 6, 6)
                p.setClipPath(recorte)
                p.setBrush(ACTIVO)
                p.drawRect(lleno)
                p.restore()
            p.setPen(TEXTO_PIEZA)
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.drawText(caja, Qt.AlignCenter, f"{texto}2  {gatillo}")

            # L1 / R1
            p.setPen(Qt.NoPen)
            p.setBrush(ACTIVO if boton else GATILLO)
            caja = QRectF(x, 30, 76, 14)
            p.drawRoundedRect(caja, 5, 5)
            p.setPen(TEXTO_PIEZA)
            p.drawText(caja, Qt.AlignCenter, f"{texto}1")

    def _touchpad(self, p, e):
        caja = QRectF(145, 56, 110, 62)
        p.setPen(QPen(PIEZA, 1.5))
        p.setBrush(ACTIVO if e and e.touchpad else TOUCHPAD)
        p.drawRoundedRect(caja, 8, 8)
        # Rayas horizontales finas, como la textura del touchpad real
        p.setPen(QPen(TOUCHPAD_RAYA, 0.6))
        y = caja.top() + 6
        while y < caja.bottom() - 4:
            p.drawLine(QPointF(caja.left() + 6, y), QPointF(caja.right() - 6, y))
            y += 4
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
        p.setPen(Qt.NoPen)
        p.setBrush(PIEZA)
        p.drawRect(QRectF(cx - grueso / 2, cy - grueso / 2, grueso, grueso))
        for caja, pulsado in brazos:
            p.setBrush(ACTIVO if pulsado else PIEZA)
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
            # Al pulsar, el botón se rellena con el color de su símbolo
            p.setPen(Qt.NoPen)
            p.setBrush(color if pulsado else PIEZA)
            p.drawEllipse(centro, radio, radio)
            p.setPen(QPen(TEXTO_PIEZA if pulsado else color, 1.8))
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
            p.setPen(Qt.NoPen)
            p.setBrush(ACTIVO if pulsado else PIEZA)
            p.drawRoundedRect(caja, 5, 5)
            p.setPen(ETIQUETA)
            p.drawText(QRectF(caja.center().x() - 25, caja.top() - 12, 50, 10), Qt.AlignCenter, texto)

        p.setPen(Qt.NoPen)
        p.setBrush(ACTIVO if e and e.ps else PIEZA)
        p.drawEllipse(QPointF(200, 140), 10, 10)
        p.setPen(TEXTO_PIEZA)
        p.setFont(QFont("Segoe UI", 7, QFont.Bold))
        p.drawText(QRectF(190, 130, 20, 20), Qt.AlignCenter, "PS")

    def _stick(self, p, centro, stick, pulsado):
        radio_hueco, radio_seta = 28, 17
        # Base blanca con un reborde interno gris
        p.setPen(QPen(BORDE, 1.5))
        p.setBrush(CUERPO)
        p.drawEllipse(centro, radio_hueco, radio_hueco)
        p.setPen(QPen(ANILLO_STICK, 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(centro, radio_hueco - 3, radio_hueco - 3)

        x = y = 0.0
        if stick is not None:
            x = (stick.x - 128) / 128 * (radio_hueco - radio_seta)
            y = (stick.y - 128) / 128 * (radio_hueco - radio_seta)
        seta = QPointF(centro.x() + x, centro.y() + y)
        p.setPen(QPen(ACTIVO, 2.5) if pulsado else Qt.NoPen)
        p.setBrush(PIEZA)
        p.drawEllipse(seta, radio_seta, radio_seta)
