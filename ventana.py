"""
Ventana principal e icono de la bandeja del sistema.
"""

from PySide6.QtCore import QRectF, QSettings, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QColorDialog, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QPushButton, QRadioButton, QSystemTrayIcon,
    QVBoxLayout, QWidget,
)

from motor import MODO_LUZ_BATERIA, MODO_LUZ_FIJO, Motor
from vista_mando import VistaMando

NOMBRE_APP = "Emulador de Control"


def crear_icono(color="#4c9aff"):
    """Icono generado por código: la silueta de un mando."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(color))
    p.drawRoundedRect(QRectF(4, 16, 56, 26), 13, 13)
    p.drawEllipse(QRectF(4, 24, 22, 32))
    p.drawEllipse(QRectF(38, 24, 22, 32))
    p.setBrush(QColor("#14161a"))
    p.drawEllipse(QRectF(14, 22, 9, 9))
    p.drawEllipse(QRectF(41, 22, 9, 9))
    p.end()
    return QIcon(pixmap)


def css_color(rgb):
    return f"background-color: rgb{tuple(rgb)}; border: 1px solid #555; border-radius: 4px;"


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOMBRE_APP)
        self.setWindowIcon(crear_icono())
        self._ajustes = QSettings("EmuladorDeControl", "EmuladorDeControl")
        self._saliendo = False
        self._aviso_bandeja_mostrado = False
        self._virtual_activo = False

        self.motor = Motor()
        self.motor.emular = self._ajustes.value("emular", True, type=bool)
        self.motor.modo_luz = self._ajustes.value("modo_luz", MODO_LUZ_BATERIA)
        color = self._ajustes.value("color_fijo", "0,0,255")
        self.motor.color_fijo = tuple(int(c) for c in color.split(","))

        self._crear_interfaz()
        self._crear_bandeja()

        self.motor.conexion_cambiada.connect(self._al_cambiar_conexion)
        self.motor.emulacion_cambiada.connect(self._al_cambiar_emulacion)
        self.motor.estado_actualizado.connect(self._al_actualizar_estado)
        self.motor.luz_actualizada.connect(self.vista.set_color_luz)
        self.motor.tasa_actualizada.connect(lambda t: self.lbl_tasa.setText(f"{t} reports/s"))

        self._al_cambiar_conexion(False, "")
        self._refrescar_emulacion()
        self.motor.start()

    # --- construcción -----------------------------------------------------

    def _crear_interfaz(self):
        # Estado de la conexión
        self.lbl_conexion = QLabel()
        self.lbl_conexion.setTextFormat(Qt.RichText)
        self.lbl_bateria = QLabel()
        self.lbl_tasa = QLabel()
        self.lbl_tasa.setStyleSheet("color: gray;")

        fila_estado = QHBoxLayout()
        fila_estado.addWidget(self.lbl_conexion)
        fila_estado.addStretch()
        fila_estado.addWidget(self.lbl_tasa)
        fila_estado.addSpacing(12)
        fila_estado.addWidget(self.lbl_bateria)

        self.vista = VistaMando()

        # Emulación
        self.btn_emular = QPushButton()
        self.btn_emular.setMinimumHeight(34)
        self.btn_emular.clicked.connect(self._alternar_emulacion)
        self.lbl_emulacion = QLabel()
        caja_emulacion = QGroupBox("Emulación")
        capa = QVBoxLayout(caja_emulacion)
        capa.addWidget(self.btn_emular)
        capa.addWidget(self.lbl_emulacion)
        capa.addStretch()

        # Barra de luz
        self.radio_bateria = QRadioButton("Según batería")
        self.radio_fijo = QRadioButton("Color fijo")
        grupo = QButtonGroup(self)
        grupo.addButton(self.radio_bateria)
        grupo.addButton(self.radio_fijo)
        (self.radio_fijo if self.motor.modo_luz == MODO_LUZ_FIJO else self.radio_bateria).setChecked(True)
        self.radio_bateria.toggled.connect(self._al_cambiar_modo_luz)
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(40, 22)
        self.btn_color.setStyleSheet(css_color(self.motor.color_fijo))
        self.btn_color.clicked.connect(self._elegir_color)
        fila_fijo = QHBoxLayout()
        fila_fijo.addWidget(self.radio_fijo)
        fila_fijo.addWidget(self.btn_color)
        fila_fijo.addStretch()
        caja_luz = QGroupBox("Barra de luz")
        capa = QVBoxLayout(caja_luz)
        capa.addWidget(self.radio_bateria)
        capa.addLayout(fila_fijo)
        capa.addStretch()

        # Vibración
        self.btn_vibrar = QPushButton("Probar vibración")
        self.btn_vibrar.clicked.connect(self.motor.probar_vibracion)
        caja_vibracion = QGroupBox("Vibración")
        capa = QVBoxLayout(caja_vibracion)
        capa.addWidget(self.btn_vibrar)
        nota = QLabel("La vibración que pidan los juegos se reenvía al mando.")
        nota.setWordWrap(True)
        nota.setStyleSheet("color: gray;")
        capa.addWidget(nota)
        capa.addStretch()

        fila_cajas = QHBoxLayout()
        fila_cajas.addWidget(caja_emulacion, 1)
        fila_cajas.addWidget(caja_luz, 1)
        fila_cajas.addWidget(caja_vibracion, 1)

        central = QWidget()
        capa = QVBoxLayout(central)
        capa.addLayout(fila_estado)
        capa.addWidget(self.vista, 1)
        capa.addLayout(fila_cajas)
        self.setCentralWidget(central)
        self.resize(640, 520)

    def _crear_bandeja(self):
        self.bandeja = QSystemTrayIcon(crear_icono(), self)
        menu = QMenu()
        accion_mostrar = QAction("Mostrar ventana", self)
        accion_mostrar.triggered.connect(self._mostrar)
        self.accion_emular = QAction("Emular Xbox 360", self, checkable=True)
        self.accion_emular.triggered.connect(self._alternar_emulacion)
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.salir)
        menu.addAction(accion_mostrar)
        menu.addAction(self.accion_emular)
        menu.addSeparator()
        menu.addAction(accion_salir)
        self.bandeja.setContextMenu(menu)
        self.bandeja.activated.connect(self._al_activar_bandeja)
        self.bandeja.setToolTip(NOMBRE_APP)
        self.bandeja.show()

    # --- reacciones al motor ----------------------------------------------

    def _al_cambiar_conexion(self, conectado, nombre):
        self.vista.set_conectado(conectado)
        self.btn_vibrar.setEnabled(conectado)
        self.lbl_bateria.setVisible(conectado)
        self.lbl_tasa.setVisible(conectado)
        if conectado:
            self.lbl_conexion.setText(f"<span style='color:#3fd1a0'>●</span> <b>{nombre}</b> · Bluetooth")
            self.bandeja.setToolTip(f"{NOMBRE_APP}\n{nombre} conectado")
        else:
            self.lbl_conexion.setText("<span style='color:#888'>●</span> Buscando DualShock 4…")
            self.bandeja.setToolTip(f"{NOMBRE_APP}\nSin mando")

    def _al_cambiar_emulacion(self, activo):
        self._virtual_activo = activo
        self._refrescar_emulacion()

    def _al_actualizar_estado(self, estado):
        self.vista.set_estado(estado)
        nivel = min(estado.bateria * 10, 100)
        self.lbl_bateria.setText(f"{'Cargando' if estado.cable else 'Batería'} {nivel}%")

    # --- acciones del usuario ---------------------------------------------

    def _alternar_emulacion(self):
        self.motor.emular = not self.motor.emular
        self._ajustes.setValue("emular", self.motor.emular)
        self._refrescar_emulacion()

    def _refrescar_emulacion(self):
        quiere = self.motor.emular
        self.btn_emular.setText("Detener emulación" if quiere else "Iniciar emulación")
        self.accion_emular.setChecked(quiere)
        if self._virtual_activo:
            self.lbl_emulacion.setText("<span style='color:#3fd1a0'>●</span> Xbox 360 virtual activo")
        elif quiere:
            self.lbl_emulacion.setText("<span style='color:#888'>●</span> Esperando al mando…")
        else:
            self.lbl_emulacion.setText("<span style='color:#888'>●</span> Xbox 360 virtual apagado")

    def _al_cambiar_modo_luz(self):
        self.motor.modo_luz = MODO_LUZ_BATERIA if self.radio_bateria.isChecked() else MODO_LUZ_FIJO
        self._ajustes.setValue("modo_luz", self.motor.modo_luz)

    def _elegir_color(self):
        color = QColorDialog.getColor(QColor(*self.motor.color_fijo), self, "Color de la barra de luz")
        if not color.isValid():
            return
        rgb = (color.red(), color.green(), color.blue())
        self.motor.color_fijo = rgb
        self.btn_color.setStyleSheet(css_color(rgb))
        self._ajustes.setValue("color_fijo", ",".join(str(c) for c in rgb))
        self.radio_fijo.setChecked(True)

    # --- bandeja y cierre -------------------------------------------------

    def _al_activar_bandeja(self, motivo):
        if motivo in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._mostrar()

    def _mostrar(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, evento):
        # Cerrar la ventana solo la esconde; la emulación sigue en la bandeja
        if self._saliendo:
            evento.accept()
            return
        evento.ignore()
        self.hide()
        if not self._aviso_bandeja_mostrado:
            self.bandeja.showMessage(
                NOMBRE_APP,
                "Sigo emulando en segundo plano. Usa el icono de la bandeja para salir.",
                crear_icono(),
                3000,
            )
            self._aviso_bandeja_mostrado = True

    def salir(self):
        self._saliendo = True
        self.motor.detener()
        self.bandeja.hide()
        QApplication.quit()
