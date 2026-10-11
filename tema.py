"""
Tema visual "Glacier White" (propuesta de Gemini, ver diseñoGemini.md).

Hoja de estilos QSS que se aplica a toda la app con app.setStyleSheet(QSS).
Propiedades personalizadas que usa:
  QPushButton[primario="true"]  -> botón de acción principal (azul)
  QLabel[secundario="true"]     -> texto secundario (gris, más pequeño)
"""

# Colores que también se usan desde Python (textos enriquecidos, icono...)
ACENTO = "#2563EB"
FONDO = "#F4F5F7"
BORDE = "#D1D5DB"
TEXTO_SECUNDARIO = "#6B7280"
EXITO = "#10B981"
AVISO = "#F59E0B"
ERROR = "#EF4444"

QSS = """
/* ===================================================================
   EMULADOR DE CONTROL - GLACIER WHITE THEME (QSS FOR PYSIDE6 / QT6)
   =================================================================== */

/* Window & Base Containers */
QMainWindow {
    background-color: #F4F5F7;
    color: #1F2937;
}

QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #1F2937;
}

/* Sidebar List (Navegación Por Pestañas) */
QListWidget#sidebar {
    background-color: #FFFFFF;
    border: none;
    border-right: 1px solid #D1D5DB;
    outline: none;
    padding-top: 8px;
}

QListWidget#sidebar::item {
    height: 40px;
    padding-left: 12px;
    color: #6B7280;
    border-radius: 6px;
    margin: 2px 8px;
}

QListWidget#sidebar::item:hover {
    background-color: #F3F4F6;
    color: #1F2937;
}

QListWidget#sidebar::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
}

/* GroupBox Container Cards */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
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
    color: #1F2937;
}

/* Standard Buttons */
QPushButton {
    background-color: #F3F4F6;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #E5E7EB;
    border-color: #9CA3AF;
}

QPushButton:pressed {
    background-color: #D1D5DB;
}

QPushButton:disabled {
    background-color: #F9FAFB;
    color: #9CA3AF;
    border-color: #E5E7EB;
}

/* Primary Accent Button Variant ([primario="true"]) */
QPushButton[primario="true"] {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #2563EB;
    font-weight: 600;
}

QPushButton[primario="true"]:hover {
    background-color: #1D4ED8;
    border-color: #1D4ED8;
}

QPushButton[primario="true"]:pressed {
    background-color: #1E40AF;
    border-color: #1E40AF;
}

/* Radio Buttons & CheckBoxes */
QRadioButton, QCheckBox {
    spacing: 8px;
    color: #1F2937;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked {
    background-color: #FFFFFF;
    border: 1px solid #9CA3AF;
    border-radius: 9px; /* Circular for Radio: (16 + 2 de borde) / 2 */
}

QCheckBox::indicator:unchecked {
    border-radius: 4px; /* Square for Checkbox */
}

QRadioButton::indicator:unchecked:hover, QCheckBox::indicator:unchecked:hover {
    border-color: #2563EB;
}

QRadioButton::indicator:checked {
    /* Punto azul dentro de un aro, mismo tamaño que sin marcar */
    background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 #2563EB, stop:0.5 #2563EB, stop:0.6 #FFFFFF, stop:1 #FFFFFF);
    border: 1px solid #2563EB;
    border-radius: 9px;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border: 1px solid #2563EB;
    border-radius: 4px;
    /* La marca ✓ irá como imagen aparte: el QSS de Qt no admite data: URIs */
}

/* Sliders (Zonas muertas, etc.) */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #E5E7EB;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #2563EB;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 2px solid #2563EB;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    border-width: 3px;
}

/* Labels */
QLabel {
    color: #1F2937;
}

QLabel[secundario="true"] {
    color: #6B7280;
    font-size: 11px;
}

/* Status Bar & Tooltips */
QStatusBar {
    background-color: #F4F5F7;
    color: #6B7280;
    border-top: 1px solid #D1D5DB;
}

QToolTip {
    background-color: #F3F4F6;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 4px 8px;
}

/* Tray Menu (QMenu) */
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    color: #1F2937;
}

QMenu::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background-color: #E5E7EB;
    margin: 4px 0;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #F4F5F7;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #D1D5DB;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9CA3AF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

"""
