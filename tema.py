"""
Tema visual "Dark Tactical" (propuesta de Gemini, ver diseñoGemini.md).

Hoja de estilos QSS que se aplica a toda la app con app.setStyleSheet(QSS).
Propiedades personalizadas que usa:
  QPushButton[primario="true"]  -> botón de acción principal (violeta)
  QLabel[secundario="true"]     -> texto secundario (gris, más pequeño)
"""

# Colores que también se usan desde Python (textos enriquecidos, icono...)
ACENTO = "#705DF2"
FONDO = "#121318"
BORDE = "#323545"
TEXTO_SECUNDARIO = "#8C90A6"
EXITO = "#22C55E"
AVISO = "#F59E0B"
ERROR = "#EF4444"

QSS = """
/* ===================================================================
   EMULADOR DE CONTROL - DARK GAMER THEME (QSS FOR PYSIDE6 / QT6)
   =================================================================== */

/* Window & Base Containers */
QMainWindow {
    background-color: #121318;
    color: #F0F2F8;
}

QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #F0F2F8;
}

/* Sidebar List (Navegación Por Pestañas) */
QListWidget#sidebar {
    background-color: #1B1C23;
    border: none;
    border-right: 1px solid #323545;
    outline: none;
    padding-top: 8px;
}

QListWidget#sidebar::item {
    height: 40px;
    padding-left: 12px;
    color: #8C90A6;
    border-radius: 6px;
    margin: 2px 8px;
}

QListWidget#sidebar::item:hover {
    background-color: #252732;
    color: #F0F2F8;
}

QListWidget#sidebar::item:selected {
    background-color: #705DF2;
    color: #FFFFFF;
    font-weight: bold;
}

/* GroupBox Container Cards */
QGroupBox {
    background-color: #1B1C23;
    border: 1px solid #323545;
    border-radius: 8px;
    margin-top: 24px;
    padding: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 4px;
    padding: 0 6px;
    background-color: transparent;
    color: #F0F2F8;
}

/* Standard Buttons */
QPushButton {
    background-color: #252732;
    color: #F0F2F8;
    border: 1px solid #323545;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #323545;
    border-color: #4A4D63;
}

QPushButton:pressed {
    background-color: #1B1C23;
}

QPushButton:disabled {
    background-color: #1B1C23;
    color: #8C90A6;
    border-color: #252732;
}

/* Primary Accent Button Variant ([primario="true"]) */
QPushButton[primario="true"] {
    background-color: #705DF2;
    color: #FFFFFF;
    border: 1px solid #705DF2;
    font-weight: 600;
}

QPushButton[primario="true"]:hover {
    background-color: #8573FF;
    border-color: #8573FF;
}

QPushButton[primario="true"]:pressed {
    background-color: #5B4BC4;
    border-color: #5B4BC4;
}

/* Radio Buttons & CheckBoxes */
QRadioButton, QCheckBox {
    spacing: 8px;
    color: #F0F2F8;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked {
    background-color: #252732;
    border: 1px solid #323545;
    border-radius: 9px; /* Circular for Radio: (16 + 2 de borde) / 2 */
}

QCheckBox::indicator:unchecked {
    border-radius: 4px; /* Square for Checkbox */
}

QRadioButton::indicator:unchecked:hover, QCheckBox::indicator:unchecked:hover {
    border-color: #705DF2;
}

QRadioButton::indicator:checked {
    /* Punto violeta dentro de un aro, mismo tamaño que sin marcar */
    background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 #705DF2, stop:0.5 #705DF2, stop:0.6 #1B1C23, stop:1 #1B1C23);
    border: 1px solid #705DF2;
    border-radius: 9px;
}

QCheckBox::indicator:checked {
    background-color: #705DF2;
    border: 1px solid #705DF2;
    border-radius: 4px;
    /* La marca ✓ irá como imagen aparte: el QSS de Qt no admite data: URIs */
}

/* Sliders (Zonas muertas, etc.) */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #252732;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #705DF2;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #F0F2F8;
    border: 2px solid #705DF2;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #FFFFFF;
    border-width: 3px;
}

/* Labels */
QLabel {
    color: #F0F2F8;
}

QLabel[secundario="true"] {
    color: #8C90A6;
    font-size: 11px;
}

/* Status Bar & Tooltips */
QStatusBar {
    background-color: #121318;
    color: #8C90A6;
    border-top: 1px solid #323545;
}

QToolTip {
    background-color: #252732;
    color: #F0F2F8;
    border: 1px solid #323545;
    border-radius: 4px;
    padding: 4px 8px;
}

/* Tray Menu (QMenu) */
QMenu {
    background-color: #1B1C23;
    border: 1px solid #323545;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    color: #F0F2F8;
}

QMenu::item:selected {
    background-color: #705DF2;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background-color: #323545;
    margin: 4px 0;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #121318;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #252732;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #323545;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

"""
