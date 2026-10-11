Para integrar el diseño de este mando DualShock 4 de color **blanco brillante con detalles en negro y símbolos clásicos de PlayStation** (con bordes de color en los botones de acción), podemos adaptar tanto la interfaz de la aplicación de escritorio como la representación vectorial en QPainter para que guarden una coherencia visual absoluta.

A continuación, te detallo los ajustes necesarios para que la interfaz pase a un modo **"Clean Storm / Glacier White"** (un estilo limpio y prémium similar al de accesorios oficiales de Sony para PC).

---

### 1. Adaptación de la Paleta de Colores (Modo Claro / Glacier White)

Invertiremos la paleta manteniendo la nitidez visual y el contraste para entornos de juego, utilizando un fondo gris clarísimo/blanco humo con tarjetas de superficie blanca pura y acentos oscuros/metálicos que combinan con el mando de la imagen:

| Token | Hex | Uso en la interfaz |
| --- | --- | --- |
| `bg-main` | `#F4F5F7` | Fondo principal de la ventana (`QMainWindow`) |
| `surface-base` | `#FFFFFF` | Tarjetas, contenedores, lista lateral (`QGroupBox`, `QListWidget`) |
| `surface-elevated` | `#E9EBEF` | Controles en reposo, entradas, cabeceras |
| `border-subtle` | `#D1D5DB` | Bordes de contenedores y separadores |
| `border-focus` | `#2563EB` | Borde activo al enfocar o seleccionar (Azul eléctrico) |
| `text-primary` | `#1F2937` | Títulos, nombres de botones y valores activos |
| `text-secondary` | `#6B7280` | Etiquetas, descripciones secundarias |
| `accent` | `#2563EB` | Acento principal (Botones primarios, selección) |
| `accent-hover` | `#1D4ED8` | Estado *hover* del acento |
| `accent-pressed` | `#1E40AF` | Estado presionado del acento |
| `success` | `#10B981` | Mando conectado, emulación activa |
| `warning` | `#F59E0B` | Esperando mando / aviso |
| `error` | `#EF4444` | Batería crítica (<15%) |
| `pad-btn-idle` | `#1F2937` | Botones del mando en reposo (Negro/Gris oscuro) |
| `pad-btn-pressed` | `#2563EB` | Botones del mando cuando se pulsan |

---

### 2. Especificaciones de QPainter para el Mando Blanco

Para que el widget de QPainter dibuje fielmente el mando de la foto, modifica los parámetros de renderizado de la siguiente manera:

* **Cuerpo Principal del Mando:**
* Color de relleno: Blanco puro (`#FFFFFF`) con un sutil degradado radial en los extremos izquierdo y derecho para simular volumen curvo (`#E2E8F0`).
* Contorno/Silueta: `#CBD5E1` con un grosor de `1.5px`.


* **Touchpad y Botones Centrales (Options, Share, PS):**
* Color de fondo del Touchpad: Negro brillante (`#111827`) con una textura de puntos sutil o líneas horizontales muy finas dibujadas con un `QPen` gris oscuro. La franja de la barra de luz se sitúa justo en el borde superior de este rectángulo.
* Botones centrales (Share, Options, PS): Negros (`#1F2937`) con iconos vectoriales en blanco.


* **Cruceta (D-Pad) y Sticks Analógicos:**
* Las direcciones de la cruceta y los capuchones de los sticks (L3/R3) son de color negro texturizado (`#1F2937`). El anillo interno que rodea la base de los sticks es blanco con un reborde interno gris claro (`#9CA3AF`).


* **Botones de Acción (✕, ○, □, △):**
* Fondo de los botones: Negro (`#1F2937`).
* Símbolos: Abajo se dibujan con líneas huecas o finas del color clásico de PlayStation exactamente como se aprecia en el mando de referencia:


* **Cruz (✕):** Símbolo en azul claro (`#3B82F6`).
* **Círculo (○):** Símbolo en rojo (`#EF4444`).
* **Cuadrado (□):** Símbolo en rosa/magenta (`#EC4899`).
* **Triángulo (△):** Símbolo en verde esmeralda (`#10B981`).




* **Gatillos (L2 / R2):**
* Visibles en la parte superior con un tono negro mate (`#374151`) que se rellena verticalmente de azul (`#2563EB`) según la presión analógica de `0` a `255`.



---

### 3. Hoja de Estilos QSS para el Tema "Glacier White"

Sustituye la hoja de estilos anterior por esta versión optimizada para un entorno limpio y claro en PySide6 / Qt 6:

```css
/* ===================================================================
   EMULADOR DE CONTROL - GLACIER WHITE / CLEAN GAMER (QSS QT6)
   =================================================================== */

QMainWindow {
    background-color: #F4F5F7;
    color: #1F2937;
}

QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #1F2937;
}

/* Sidebar List */
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
    background-color: #FFFFFF;
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

/* Primary Accent Button ([primario="true"]) */
QPushButton[primario="true"] {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #2563EB;
    font-weight: 600;
}

QPushButton[primario="true"]:hover {
    background-color: #1D4ED8;
}

QPushButton[primario="true"]:pressed {
    background-color: #1E40AF;
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
    border-radius: 8px;
}

QCheckBox::indicator:unchecked {
    border-radius: 4px;
}

QRadioButton::indicator:unchecked:hover, QCheckBox::indicator:unchecked:hover {
    border-color: #2563EB;
}

QRadioButton::indicator:checked {
    background-color: #2563EB;
    border: 3px solid #FFFFFF;
    border-radius: 8px;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border: 1px solid #2563EB;
    border-radius: 4px;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
}

/* Sliders */
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
    background-color: #FFFFFF;
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

```

---

### 4. Maqueta HTML/CSS Interactiva (Estilo Blanco Glaciar)

Guarda este código como `preview_white.html` para comprobar en el navegador cómo armoniza la interfaz clara con el concepto del mando blanco y negro:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Emulador de Control - Glacier White Preview</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: #E5E7EB;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .app-window {
      width: 640px;
      height: 520px;
      background-color: #F4F5F7;
      border: 1px solid #D1D5DB;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 12px 32px rgba(0,0,0,0.15);
    }

    .statusbar {
      height: 28px;
      background-color: #F4F5F7;
      border-bottom: 1px solid #D1D5DB;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      font-size: 11px;
      color: #6B7280;
    }
    .status-badge { display: flex; align-items: center; gap: 6px; color: #1F2937; font-weight: 600; }
    .dot-online { width: 8px; height: 8px; background-color: #10B981; border-radius: 4px; }

    .app-body { display: flex; flex: 1; }

    .sidebar {
      width: 140px;
      background-color: #FFFFFF;
      border-right: 1px solid #D1D5DB;
      padding-top: 8px;
    }
    .nav-item {
      padding: 10px 12px;
      font-size: 12px;
      color: #6B7280;
      cursor: pointer;
      margin: 2px 8px;
      border-radius: 6px;
    }
    .nav-item.active { background-color: #2563EB; color: #FFFFFF; font-weight: 600; }
    .nav-item:hover:not(.active) { background-color: #F3F4F6; color: #1F2937; }

    .main-content { flex: 1; padding: 12px; display: flex; flex-direction: column; gap: 12px; }

    .controller-canvas {
      height: 210px;
      background-color: #FFFFFF;
      border: 1px solid #D1D5DB;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      position: relative;
    }
    /* Representación simulada del mando blanco */
    .pad-illustration {
      width: 260px;
      height: 140px;
      border: 2px solid #CBD5E1;
      background-color: #FFFFFF;
      border-radius: 40px;
      position: relative;
      display: flex;
      justify-content: center;
      box-shadow: inset 0 2px 6px rgba(0,0,0,0.05);
    }
    .lightbar-preview {
      width: 70px;
      height: 6px;
      background-color: #2563EB;
      border-radius: 0 0 4px 4px;
      box-shadow: 0 0 6px rgba(37, 99, 235, 0.5);
    }

    .controls-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

    .card {
      background-color: #FFFFFF;
      border: 1px solid #D1D5DB;
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .card-title { font-size: 12px; font-weight: 600; color: #1F2937; }

    .btn {
      background-color: #F3F4F6;
      color: #1F2937;
      border: 1px solid #D1D5DB;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      text-align: center;
    }
    .btn-primary { background-color: #2563EB; border-color: #2563EB; color: #FFF; font-weight: 600; }
    .btn-primary:hover { background-color: #1D4ED8; }

    .radio-group { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #6B7280; }
    .radio-item { display: flex; align-items: center; gap: 6px; color: #1F2937; }
  </style>
</head>
<body>

  <div class="app-window">
    <div class="statusbar">
      <div class="status-badge">
        <div class="dot-online"></div>
        DualShock 4 v2 (Glacier White) · Bluetooth
      </div>
      <div>702 Hz &nbsp;|&nbsp; Batería: 85%</div>
    </div>

    <div class="app-body">
      <div class="sidebar">
        <div class="nav-item active">🕹️ Mando</div>
        <div class="nav-item">🎯 Ajustes Sticks</div>
        <div class="nav-item">🔀 Remapeo</div>
        <div class="nav-item">🛡️ HidHide</div>
      </div>

      <div class="main-content">
        <div class="controller-canvas">
          <div class="pad-illustration">
            <div class="lightbar-preview"></div>
          </div>
          <span style="font-size: 10px; color: #6B7280; margin-top: 8px;">[Simulación QPainter con Mando Blanco]</span>
        </div>

        <div class="controls-grid">
          <div class="card">
            <div class="card-title">Emulación Xbox 360</div>
            <div style="font-size: 11px; color: #10B981; font-weight: 600;">● Xbox 360 Virtual Activo</div>
            <button class="btn btn-primary">Detener Emulación</button>
          </div>

          <div class="card">
            <div class="card-title">Barra de Luz & Vibración</div>
            <div class="radio-group">
              <label class="radio-item"><input type="radio" name="light"> Según Batería</label>
              <label class="radio-item"><input type="radio" name="light" checked> Color Fijo (#2563EB)</label>
            </div>
            <button class="btn" style="margin-top:2px;">Probar Vibración</button>
          </div>
        </div>
      </div>
    </div>
  </div>

</body>
</html>

```