Aquí tienes una propuesta completa de diseño de interfaz de usuario pensada para ser **100% ejecutable en PySide6 / Qt 6** con widgets tradicionales.

---

## 1. Concepto visual

El concepto se denomina **"Gamer Precision / Dark Tactical"**. Combina la estética minimalista y profesional de utilitarios modernos (como *Xbox Accessories* o *SteelSeries GG*) con la densidad de información clara que requiere una herramienta como *DS4Windows*. El tono visual es un gris carbón profundo con acentos en violeta/índigo neón para transmitir capacidad técnica sin saturar la vista durante partidas nocturnas.

---

## 2. Paleta de colores

### Modo Oscuro (Principal)

| Token | Hex | Uso |
| --- | --- | --- |
| `bg-main` | `#121318` | Fondo principal de la ventana (`QMainWindow`) |
| `surface-base` | `#1B1C23` | Tarjetas, contenedores, lista lateral (`QGroupBox`, `QListWidget`) |
| `surface-elevated` | `#252732` | Controles en reposo, entradas, cabeceras (`QPushButton`, `QSlider`) |
| `border-subtle` | `#323545` | Bordes de contenedores y separadores |
| `border-focus` | `#705DF2` | Borde activo al enfocar con teclado o seleccionar |
| `text-primary` | `#F0F2F8` | Títulos, nombres de botones y valores activos |
| `text-secondary` | `#8C90A6` | Etiquetas, descripciones secundarias y rangos |
| `accent` | `#705DF2` | Acento principal (brillo activo, selección, botón primario) |
| `accent-hover` | `#8573FF` | Estado *hover* de elementos primarios |
| `accent-pressed` | `#5B4BC4` | Estado presionado de elementos primarios |
| `success` | `#22C55E` | Mando conectado, emulación activa, batería saludable |
| `warning` | `#F59E0B` | Esperando mando, aviso de latencia |
| `error` | `#EF4444` | Batería crítica (<15%), error de emulación |
| `pad-btn-idle` | `#2D303E` | Botones del mando dibujados sin pulsar |
| `pad-btn-pressed` | `#8573FF` | Botones del mando cuando el usuario los presiona |

### Modo Claro (Opcional / Acompañamiento)

| Token | Hex | Uso |
| --- | --- | --- |
| `bg-main` | `#F3F4F8` | Fondo principal de la ventana |
| `surface-base` | `#FFFFFF` | Tarjetas y contenedores |
| `surface-elevated` | `#E8EAF0` | Controles en reposo |
| `border-subtle` | `#D2D6E0` | Bordes |
| `text-primary` | `#111827` | Texto principal |
| `text-secondary` | `#6B7280` | Texto secundario |
| `accent` | `#6366F1` | Acento principal |

---

## 3. Tipografía

Utilizaremos **Segoe UI** por ser la tipografía nativa del sistema en Windows 10/11, garantizando un renderizado perfecto con subpíxeles sin descargar fuentes externas. Como alternativa moderna, se puede emplear **Inter**.

* **Título de Sección / Encabezado:** Segoe UI, Semibold (600), `14px` (`18px` de altura de línea equivalente).
* **Texto del Cuerpo / Botones:** Segoe UI, Regular (400) / Medium (500), `12px`.
* **Etiquetas / Descripciones Secundarias:** Segoe UI, Regular (400), `11px`.
* **Métricas Telegráficas (Hz, Batería, Latencia):** Segoe UI / Consolas, Semibold (600), `11px` (Monoespaciada para evitar saltos al cambiar valores).

---

## 4. Layout y arquitectura de la ventana

Para integrar las funciones actuales y permitir la expansión futura (Zonas muertas, Remapeo, HidHide, Inicio automático) sin saturar la vista, dividimos la interfaz en una **Navegación Lateral Izquierda (Sidebar)** y un **Panel de Contenido Principal**.

### Estructura General de la Ventana (640 × 520 px)

```
+-------------------------------------------------------------------------+
| [●] DualShock 4 v2 · Bluetooth    | 700 Hz | [⚡ 60%] | Statusbar (28px)|
+------------+------------------------------------------------------------+
| SECCIONES  |  PANEL PRINCIPAL (470px wide)                              |
| (140px)    |                                                            |
|            |  +------------------------------------------------------+  |
| [🕹️] Vista |  |                                                      |  |
|      Previa|  |            CANVAS QPAINTER DEL DS4                   |  |
|            |  |                  (200px height)                      |  |
| [⚙️] Ajustes|  |                                                      |  |
|      Emul. |  +------------------------------------------------------+  |
|            |                                                            |  |
| [🎯] Sticks|  +-----------------------+ +----------------------------+  |
|      & Zonas|  | Emulación             | | Barra de Luz & Vibración   |  |
|            |  | [ Mando Xbox 360  ]   | | ( ) Según batería          |  |
| [🔀] Mapeo  |  | [ Detener Emulación ] | | (*) Color fijo   [ #705DF2 ]|  |
|            |  |                       | | [ Probar Vibración ]       |  |
| [🛡️] Ocultar|  +-----------------------+ +----------------------------+  |
|      (Hid) |                                                            |  |
+------------+------------------------------------------------------------+

```

### Detalle del Panel Principal: Tab "Vista Previa" (Mando en vivo)

```
+-------------------------------------------------------------------------+
|  CANVAS DEL MANDO (QPainter Widget)                                     |
|  - Dimensiones: Auto-fit ~450x190px (Margen interno 12px)                 |
|  - Muestra animación gráfica de botones, gatillos y sticks              |
+-------------------------------------------------------------------------+
|  Fila Inferior de Ajustes Rápidos (Grid de 2 Columnas)                  |
|                                                                         |
|  +-- QGroupBox: "Emulación Xbox 360" -+ +-- QGroupBox: "Barra de Luz" --+ |
|  | Estado: ● Emulando como Xbox 360   | | ( ) Según batería (Verde->Rojo)| |
|  |                                    | | (*) Color fijo [ #705DF2 ]     | |
|  | [ Iniciar / Detener Emulación ]    | |                                | |
|  |  (btn primario [primario="true"])  | | [ Probar Vibración ]           | |
|  +------------------------------------+ +--------------------------------+ |
+-------------------------------------------------------------------------+

```

### Detalle del Tab "Ajustes / Perfil" (Futuras funciones)

```
+-------------------------------------------------------------------------+
|  +-- QGroupBox: "Ajustes del Sistema" --------------------------------+ |
|  | [X] Ocultar mando real a los juegos (HidHide driver instalado)      | |
|  | [X] Iniciar automáticamente con Windows (en la bandeja)             | |
|  | [ ] Minimizar a la bandeja al cerrar la ventana                     | |
|  +--------------------------------------------------------------------+ |
|                                                                         |
|  +-- QGroupBox: "Comportamiento del Mando" ---------------------------+ |
|  | Tiempo de apagado por inactividad: [ 10 minutos  |v]                | |
|  +--------------------------------------------------------------------+ |
+-------------------------------------------------------------------------+

```

---

## 5. Indicaciones concretas para el dibujo del mando (`QPainter`)

El widget del mando personalizado dibujará directamente mediante primitivas de `QPainter` con suavizado habilitado (`QPainter::Antialiasing`).

### Colores del Vector

* **Cuerpo del mando:** `#20222B` (Gris oscuro mate).
* **Contorno/Silueta:** `#323545` con un grosor de `1.5px`.
* **Grips/Empuñaduras:** `#181920` (Un tono más oscuro con textura simulated via `QPen` punteado suave).
* **Botones en reposo:** `#2D303E`.
* **Símbolos en reposo:** `#8C90A6`.

### Iluminación de Botones al Pulsar

* **Cross (✕):** Relleno `#2563EB` (Azul), Símbolo `#FFFFFF`.
* **Circle (○):** Relleno `#DC2626` (Rojo), Símbolo `#FFFFFF`.
* **Square (□):** Relleno `#DB2777` (Rosa/Magenta), Símbolo `#FFFFFF`.
* **Triangle (△):** Relleno `#059669` (Verde), Símbolo `#FFFFFF`.
* **D-Pad, L1, R1, Share, Options, PS:** Relleno `#705DF2` (Acento), texto o icono `#FFFFFF`.

### Representación de Gatillos (L2 / R2) e Indicador de Luz

* **Gatillos (L2/R2):** Dibuja rectángulos redondeados verticales arriba de L1/R1. El fondo del canal es `#1B1C23`. La barra de progreso interna sube proporcionalmente de `0` a `255` rellenándose con `#705DF2`. Muestra el valor numérico en texto pequeño `9px` sobre el indicador.
* **Barra de Luz (Lightbar):** Una franja superior curva central sobre el Touchpad. Usa un degradado lineal (`QLinearGradient`) usando el color configurado por el usuario enfocado hacia el centro para simular un resplandor LED.

### Sticks Analógicos (L3 / R3)

* Dibuja los círculos contenedores en `#171821`.
* Dibuja la cabeza del stick como un círculo centrado en `#373A4B`.
* **Movimiento:** Desplaza el centro del círculo de la cabeza usando coordenadas polares ajustadas a las lecturas analógicas del mando.
* **Presionado (L3/R3):** Achica ligeramente el radio del stick (efecto profundidad) y cambia el borde externo a `#705DF2`.

### Estado Desconectado ("Buscando mando…")

1. Configura la opacidad global del painter en `0.35` (`painter.setOpacity(0.35)`).
2. Dibuja el mando con los colores por defecto.
3. Restablece la opacidad a `1.0` y dibuja un texto central en `14px Bold` color `#F0F2F8` con fondo semitransparente `#1B1C23` (redondeado `8px`) que diga: **"Esperando conexión Bluetooth…"**.

---

## 6. Hoja de Estilos QSS Completa

Copia y pega este bloque QSS directamente en tu aplicación mediante `app.setStyleSheet(...)`:

```css
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
    background-color: #1B1C23;
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
    border-radius: 8px; /* Circular for Radio */
}

QCheckBox::indicator:unchecked {
    border-radius: 4px; /* Square for Checkbox */
}

QRadioButton::indicator:unchecked:hover, QCheckBox::indicator:unchecked:hover {
    border-color: #705DF2;
}

QRadioButton::indicator:checked {
    background-color: #705DF2;
    border: 3px solid #1B1C23;
    border-radius: 8px;
}

QCheckBox::indicator:checked {
    background-color: #705DF2;
    border: 1px solid #705DF2;
    border-radius: 4px;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
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

```

---

## 7. Microdetalles y manejo de estados

1. **Estado Conectado vs. Emulando:**
* **Solo Conectado:** Indicador en la barra de estado muestra `● DualShock 4 v2 (Bluetooth)` con punto `#22C55E` (Verde). El botón de emulación muestra `"Iniciar Emulación Xbox 360"`.
* **Emulando Activo:** El indicador de emulación muestra `● Xbox 360 Virtual Activo` en verde. El botón cambia a estado secundario/peligro suave con texto `"Detener Emulación"`.


2. **Alertas de Batería Baja:**
* Al bajar del **15%**, el texto de batería en la barra de estado se vuelve `#EF4444` (Rojo), añade un icono `[⚠️ 12%]` y la barra de luz del mando conmuta automáticamente a un parpadeo tenue rojo si la opción *"Según batería"* está activa.


3. **Estado de Búsqueda:**
* Cuando no hay mando activo, deshabilita los controles de emulación y vibración (`setEnabled(False)`) para dar retroalimentación clara de que la app requiere hardware presente.



---

## 8. Maqueta HTML/CSS Interactiva

Guarda este código en un archivo `.html` (por ejemplo, `preview.html`) y ábrelo en cualquier navegador web. Utiliza únicamente propiedades transferibles al modelo de caja de Qt QSS:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Emulador de Control - Layout Preview</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: #0B0C0E;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    /* Contenedor principal imitando la ventana PySide (640x520) */
    .app-window {
      width: 640px;
      height: 520px;
      background-color: #121318;
      border: 1px solid #323545;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 12px 32px rgba(0,0,0,0.6);
    }

    /* Barra de Estado Top */
    .statusbar {
      height: 28px;
      background-color: #121318;
      border-bottom: 1px solid #323545;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      font-size: 11px;
      color: #8C90A6;
    }
    .status-badge { display: flex; align-items: center; gap: 6px; color: #F0F2F8; font-weight: 600; }
    .dot-online { width: 8px; height: 8px; background-color: #22C55E; border-radius: 4px; }

    /* Cuerpo Principal */
    .app-body { display: flex; flex: 1; }

    /* Sidebar Navigation */
    .sidebar {
      width: 140px;
      background-color: #1B1C23;
      border-right: 1px solid #323545;
      padding-top: 8px;
    }
    .nav-item {
      padding: 10px 12px;
      font-size: 12px;
      color: #8C90A6;
      cursor: pointer;
      margin: 2px 8px;
      border-radius: 6px;
    }
    .nav-item.active { background-color: #705DF2; color: #FFFFFF; font-weight: 600; }
    .nav-item:hover:not(.active) { background-color: #252732; color: #F0F2F8; }

    /* Canvas area / Main Content */
    .main-content { flex: 1; padding: 12px; display: flex; flex-direction: column; gap: 12px; }

    .controller-canvas {
      height: 210px;
      background-color: #1B1C23;
      border: 1px solid #323545;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      position: relative;
    }
    .pad-illustration {
      width: 260px;
      height: 140px;
      border: 2px solid #323545;
      background-color: #20222B;
      border-radius: 40px;
      position: relative;
      display: flex;
      justify-content: center;
    }
    .lightbar-preview {
      width: 70px;
      height: 6px;
      background-color: #705DF2;
      border-radius: 0 0 4px 4px;
      box-shadow: 0 0 8px #705DF2;
    }

    /* Grid de Ajustes Inferiores */
    .controls-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

    .card {
      background-color: #1B1C23;
      border: 1px solid #323545;
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .card-title { font-size: 12px; font-weight: 600; color: #F0F2F8; }

    /* Componentes de Formulario UI */
    .btn {
      background-color: #252732;
      color: #F0F2F8;
      border: 1px solid #323545;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      text-align: center;
    }
    .btn-primary { background-color: #705DF2; border-color: #705DF2; color: #FFF; font-weight: 600; }
    .btn-primary:hover { background-color: #8573FF; }

    .radio-group { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #8C90A6; }
    .radio-item { display: flex; align-items: center; gap: 6px; color: #F0F2F8; }
  </style>
</head>
<body>

  <div class="app-window">
    <!-- Status Bar -->
    <div class="statusbar">
      <div class="status-badge">
        <div class="dot-online"></div>
        DualShock 4 v2 · Bluetooth
      </div>
      <div>702 Hz &nbsp;|&nbsp; Batería: 60%</div>
    </div>

    <!-- Main Body -->
    <div class="app-body">
      <!-- Sidebar Navigation -->
      <div class="sidebar">
        <div class="nav-item active">🕹️ Mando</div>
        <div class="nav-item">🎯 Ajustes Sticks</div>
        <div class="nav-item">🔀 Remapeo</div>
        <div class="nav-item">🛡️ HidHide</div>
      </div>

      <!-- Content Area -->
      <div class="main-content">
        <!-- QPainter Controller Area -->
        <div class="controller-canvas">
          <div class="pad-illustration">
            <div class="lightbar-preview"></div>
          </div>
          <span style="font-size: 10px; color: #8C90A6; margin-top: 8px;">[Simulación QPainter Canvas Active]</span>
        </div>

        <!-- Controls Row -->
        <div class="controls-grid">
          <div class="card">
            <div class="card-title">Emulación Xbox 360</div>
            <div style="font-size: 11px; color: #22C55E;">● Xbox 360 Virtual Activo</div>
            <button class="btn btn-primary">Detener Emulación</button>
          </div>

          <div class="card">
            <div class="card-title">Barra de Luz & Vibración</div>
            <div class="radio-group">
              <label class="radio-item"><input type="radio" name="light"> Según Batería</label>
              <label class="radio-item"><input type="radio" name="light" checked> Color Fijo (#705DF2)</label>
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