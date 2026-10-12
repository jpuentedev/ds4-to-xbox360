"""
Ventana principal e icono de la bandeja del sistema.
"""

import subprocess

from PySide6.QtCore import QRectF, QSettings, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QColorDialog, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QListWidget, QMenu, QPushButton, QRadioButton, QSlider, QStackedWidget, QSystemTrayIcon,
    QVBoxLayout, QWidget,
)

from motor import MODO_LUZ_BATERIA, MODO_LUZ_FIJO, Motor
import hidhide
from tema import ACENTO, AVISO, BORDE, ERROR, EXITO, FONDO, TEXTO_SECUNDARIO
from vista_mando import VistaMando, VistaZonaMuerta

NOMBRE_APP = "Emulador de Control"
BATERIA_CRITICA = 15  # % por debajo del cual la batería se muestra en rojo
ZONA_MUERTA_MAX = 30  # % máximo de los deslizadores


def crear_icono(color=ACENTO):
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
    p.setBrush(QColor(FONDO))
    p.drawEllipse(QRectF(14, 22, 9, 9))
    p.drawEllipse(QRectF(41, 22, 9, 9))
    p.end()
    return QIcon(pixmap)


def css_color(rgb):
    return f"background-color: rgb{tuple(rgb)}; border: 1px solid {BORDE}; border-radius: 4px; padding: 0; min-height: 0;"


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOMBRE_APP)
        self.setWindowIcon(crear_icono())
        self._ajustes = QSettings("EmuladorDeControl", "EmuladorDeControl")
        self._saliendo = False
        self._aviso_bandeja_mostrado = False
        self._virtual_activo = False

        # Antes de buscar el mando: si HidHide lo oculta, que nos deje verlo
        try:
            hidhide.asegurar_permiso()
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
            pass  # la página de HidHide mostrará el problema

        self.motor = Motor()
        self.motor.emular = self._ajustes.value("emular", True, type=bool)
        self.motor.modo_luz = self._ajustes.value("modo_luz", MODO_LUZ_BATERIA)
        color = self._ajustes.value("color_fijo", "0,0,255")
        self.motor.color_fijo = tuple(int(c) for c in color.split(","))
        self.motor.zona_muerta_izq = self._ajustes.value("zona_muerta_izq", 0, type=int) / 100
        self.motor.zona_muerta_der = self._ajustes.value("zona_muerta_der", 0, type=int) / 100

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
        self.lbl_bateria.setTextFormat(Qt.RichText)
        self.lbl_tasa = QLabel()
        self.lbl_tasa.setProperty("secundario", True)

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

        # Vibración (comparte caja con la barra de luz)
        self.btn_vibrar = QPushButton("Probar vibración")
        self.btn_vibrar.clicked.connect(self.motor.probar_vibracion)
        nota = QLabel("La vibración que pidan los juegos se reenvía al mando.")
        nota.setWordWrap(True)
        nota.setProperty("secundario", True)

        caja_luz = QGroupBox("Barra de luz y vibración")
        capa = QVBoxLayout(caja_luz)
        capa.addWidget(self.radio_bateria)
        capa.addLayout(fila_fijo)
        capa.addWidget(self.btn_vibrar)
        capa.addWidget(nota)
        capa.addStretch()

        # Dos columnas del mismo ancho
        fila_cajas = QHBoxLayout()
        fila_cajas.setSpacing(12)
        fila_cajas.addWidget(caja_emulacion, 1)
        fila_cajas.addWidget(caja_luz, 1)

        # Zonas muertas
        self.zona_izq = VistaZonaMuerta()
        self.zona_der = VistaZonaMuerta()
        caja_zonas = QGroupBox("Zonas muertas")
        capa = QVBoxLayout(caja_zonas)
        fila = QHBoxLayout()
        fila.setSpacing(12)
        fila.addLayout(self._control_zona("Stick izquierdo", "zona_muerta_izq", self.zona_izq), 1)
        fila.addLayout(self._control_zona("Stick derecho", "zona_muerta_der", self.zona_der), 1)
        capa.addLayout(fila)
        nota = QLabel("Gris: posición real del stick · Azul: lo que recibe el juego · Rojo: zona muerta")
        nota.setProperty("secundario", True)
        nota.setWordWrap(True)
        capa.addWidget(nota)

        # Páginas: cada una es un QWidget dentro del QStackedWidget
        pagina_mando = QWidget()
        capa = QVBoxLayout(pagina_mando)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.addWidget(self.vista, 1)
        capa.addLayout(fila_cajas)

        pagina_sticks = QWidget()
        capa = QVBoxLayout(pagina_sticks)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.addWidget(caja_zonas)
        capa.addStretch()

        pagina_hidhide = self._crear_pagina_hidhide()

        self.paginas = QStackedWidget()
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")  # así le aplica el estilo QListWidget#sidebar
        self.sidebar.setFixedWidth(160)
        for texto, pagina in (
            ("🕹️  Mando", pagina_mando),
            ("🎯  Sticks", pagina_sticks),
            ("🛡️  HidHide", pagina_hidhide),
        ):
            self.sidebar.addItem(texto)
            self.paginas.addWidget(pagina)
        # El estado de HidHide se consulta al entrar en su página (tarda ~0,3 s)
        self.sidebar.currentRowChanged.connect(
            lambda fila: self._refrescar_hidhide() if self.paginas.widget(fila) is pagina_hidhide else None
        )
        # Elegir en la lista cambia la página; también recordamos la última
        self.sidebar.currentRowChanged.connect(self.paginas.setCurrentIndex)
        self.sidebar.currentRowChanged.connect(lambda fila: self._ajustes.setValue("pagina", fila))
        self.sidebar.setCurrentRow(self._ajustes.value("pagina", 0, type=int))

        contenido = QVBoxLayout()
        contenido.setContentsMargins(12, 8, 12, 12)
        contenido.addLayout(fila_estado)
        contenido.addWidget(self.paginas, 1)

        central = QWidget()
        capa = QHBoxLayout(central)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.setSpacing(0)
        capa.addWidget(self.sidebar)
        capa.addLayout(contenido, 1)
        self.setCentralWidget(central)
        self.resize(800, 540)

    def _crear_pagina_hidhide(self):
        self.lbl_hh_instalado = QLabel()
        self.lbl_hh_ds4 = QLabel()
        self.lbl_hh_lista = QLabel()
        for lbl in (self.lbl_hh_instalado, self.lbl_hh_ds4, self.lbl_hh_lista):
            lbl.setTextFormat(Qt.RichText)

        self.btn_hidhide = QPushButton()
        self.btn_hidhide.setMinimumHeight(34)
        self.btn_hidhide.clicked.connect(self._alternar_hidhide)
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self._refrescar_hidhide)
        fila_botones = QHBoxLayout()
        fila_botones.addWidget(self.btn_hidhide, 1)
        fila_botones.addWidget(btn_actualizar)

        self.lbl_hh_nota = QLabel()
        self.lbl_hh_nota.setProperty("secundario", True)
        self.lbl_hh_nota.setWordWrap(True)
        self.lbl_hh_nota.setTextInteractionFlags(Qt.TextSelectableByMouse)

        caja = QGroupBox("Ocultar el DS4 a los juegos")
        capa = QVBoxLayout(caja)
        capa.addWidget(self.lbl_hh_instalado)
        capa.addWidget(self.lbl_hh_ds4)
        capa.addWidget(self.lbl_hh_lista)
        capa.addSpacing(6)
        capa.addLayout(fila_botones)
        capa.addWidget(self.lbl_hh_nota)

        pagina = QWidget()
        capa = QVBoxLayout(pagina)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.addWidget(caja)
        capa.addStretch()
        return pagina

    def _control_zona(self, titulo, atributo, vista):
        """Deslizador + dibujo para la zona muerta de un stick (atributo del motor)."""
        porcentaje = round(getattr(self.motor, atributo) * 100)
        etiqueta = QLabel()
        deslizador = QSlider(Qt.Horizontal)
        deslizador.setRange(0, ZONA_MUERTA_MAX)

        def al_cambiar(valor):
            setattr(self.motor, atributo, valor / 100)
            self._ajustes.setValue(atributo, valor)
            etiqueta.setText(f"{titulo}: <b>{valor}%</b>")
            vista.set_zona(valor / 100)

        deslizador.valueChanged.connect(al_cambiar)
        deslizador.setValue(porcentaje)
        al_cambiar(porcentaje)  # setValue no avisa si el valor no cambia (p. ej. 0)

        columna = QVBoxLayout()
        columna.addWidget(vista, 0, Qt.AlignHCenter)
        columna.addWidget(etiqueta)
        columna.addWidget(deslizador)
        return columna

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
        if not conectado:
            self.zona_izq.set_stick(None)
            self.zona_der.set_stick(None)
        self.btn_vibrar.setEnabled(conectado)
        self.lbl_bateria.setVisible(conectado)
        self.lbl_tasa.setVisible(conectado)
        if conectado:
            self.lbl_conexion.setText(f"<span style='color:{EXITO}'>●</span> <b>{nombre}</b> · Bluetooth")
            self.bandeja.setToolTip(f"{NOMBRE_APP}\n{nombre} conectado")
        else:
            self.lbl_conexion.setText(f"<span style='color:{TEXTO_SECUNDARIO}'>●</span> Buscando DualShock 4…")
            self.bandeja.setToolTip(f"{NOMBRE_APP}\nSin mando")

    def _al_cambiar_emulacion(self, activo):
        self._virtual_activo = activo
        self._refrescar_emulacion()

    def _al_actualizar_estado(self, estado):
        self.vista.set_estado(estado)
        self.zona_izq.set_stick(estado.stick_izq)
        self.zona_der.set_stick(estado.stick_der)
        nivel = min(estado.bateria * 10, 100)
        texto = f"{'Cargando' if estado.cable else 'Batería'} {nivel}%"
        if not estado.cable and nivel < BATERIA_CRITICA:
            texto = f"<span style='color:{ERROR}'><b>{texto}</b></span>"
        self.lbl_bateria.setText(texto)

    # --- acciones del usuario ---------------------------------------------

    def _alternar_emulacion(self):
        self.motor.emular = not self.motor.emular
        self._ajustes.setValue("emular", self.motor.emular)
        self._refrescar_emulacion()

    def _refrescar_emulacion(self):
        quiere = self.motor.emular
        self.btn_emular.setText("Detener emulación" if quiere else "Iniciar emulación")
        # Azul para invitar a iniciar; normal cuando ya está emulando.
        # Qt no reaplica el QSS al cambiar una propiedad: hay que "repulirlo".
        self.btn_emular.setProperty("primario", not quiere)
        self.btn_emular.style().unpolish(self.btn_emular)
        self.btn_emular.style().polish(self.btn_emular)
        self.accion_emular.setChecked(quiere)
        if self._virtual_activo:
            self.lbl_emulacion.setText(f"<span style='color:{EXITO}'>●</span> Xbox 360 virtual activo")
        elif quiere:
            self.lbl_emulacion.setText(f"<span style='color:{AVISO}'>●</span> Esperando al mando…")
        else:
            self.lbl_emulacion.setText(f"<span style='color:{TEXTO_SECUNDARIO}'>●</span> Xbox 360 virtual apagado")

    def _refrescar_hidhide(self):
        def punto(color, texto):
            return f"<span style='color:{color}'>●</span> {texto}"

        try:
            estado = hidhide.leer_estado()
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
            self.lbl_hh_instalado.setText(punto(ERROR, f"No se pudo consultar HidHide: {error}"))
            self.lbl_hh_ds4.clear()
            self.lbl_hh_lista.clear()
            self.btn_hidhide.setEnabled(False)
            return

        self.btn_hidhide.setEnabled(estado.instalado)
        if not estado.instalado:
            self.lbl_hh_instalado.setText(punto(ERROR, "HidHide no está instalado"))
            self.lbl_hh_ds4.clear()
            self.lbl_hh_lista.clear()
            self.btn_hidhide.setText("Ocultar DS4 a los juegos")
            self.lbl_hh_nota.setText("Instálalo con:  winget install --id Nefarius.HidHide  y reinicia el PC.")
            return

        self.lbl_hh_instalado.setText(punto(EXITO, "HidHide instalado"))
        if not estado.ds4_conectados:
            self.lbl_hh_ds4.setText(punto(TEXTO_SECUNDARIO, "DS4 no detectado: conéctalo para poder ocultarlo"))
        elif estado.ds4_oculto:
            self.lbl_hh_ds4.setText(punto(EXITO, "DS4 oculto: los juegos solo ven el Xbox 360"))
        else:
            self.lbl_hh_ds4.setText(punto(AVISO, "DS4 visible: los juegos pueden ver los dos mandos"))
        if estado.emulador_permitido:
            self.lbl_hh_lista.setText(punto(EXITO, "El emulador está en la lista blanca (puede ver el DS4)"))
        elif estado.activo:
            # Pasa p. ej. con el .exe nuevo si HidHide ya estaba activo de antes
            self.lbl_hh_lista.setText(punto(ERROR, "El emulador no está en la lista blanca: no puede ver el DS4"))
        else:
            self.lbl_hh_lista.setText(punto(TEXTO_SECUNDARIO, "El emulador aún no está en la lista blanca"))

        # "Dejar de ocultar" solo si ya está todo bien; si no, el botón lo arregla
        # (ocultar_ds4 añade el emulador a la lista blanca antes de ocultar)
        todo_bien = estado.activo and estado.emulador_permitido
        if todo_bien:
            texto = "Dejar de ocultar"
        elif estado.activo:
            texto = "Permitir al emulador ver el DS4"
        else:
            texto = "Ocultar DS4 a los juegos"
        self.btn_hidhide.setText(texto)
        self.btn_hidhide.setProperty("primario", not todo_bien)
        self.btn_hidhide.style().unpolish(self.btn_hidhide)
        self.btn_hidhide.style().polish(self.btn_hidhide)
        self._hidhide_activo = todo_bien
        self.lbl_hh_nota.setText(
            "Sigue activo aunque cierres la app: si lo dejas activado y cierras el emulador, "
            "los juegos no verán ningún mando hasta que lo vuelvas a abrir."
        )

    def _alternar_hidhide(self):
        try:
            if getattr(self, "_hidhide_activo", False):
                hidhide.dejar_de_ocultar()
            else:
                hidhide.ocultar_ds4()
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            self.lbl_hh_nota.setText(f"Error: {error}")
            return
        self._refrescar_hidhide()

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
