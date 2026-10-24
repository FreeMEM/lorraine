# 06. Interfaz de usuario

Las ventanas, menús, atajos, teclado, eventos y mensajes de Lorraine Calc y Lorraine Write. Es una **propuesta de
diseño**, previa al código: los números de evento, los atajos y los textos se fijan al construir cada hito y aquí se
ponen al día.

Cada ventana principal se define en su `.dashui` (editor visual de MUI de Dash: `calc/calc.dashui`,
`write/write.dashui`) y su comportamiento en `calc/calc.dash` y `write/write.dash`. Las piezas comunes (diálogos de
abrir y guardar, avisos, preferencias, Acerca de) están en `core/interfaz`.

**Lo que hoy no da Dash** se marca con la tarea que lo añade: **[D11]**, **[D13]**... (ver [13](13_DASH.md)). Lo que
hace falta y aún no tiene número en 13 se marca **[D nueva]** y está en la lista del § 8.

## 1. Criterios comunes

- **Atajos de menú:** los de la *Amiga User Interface Style Guide* donde existen (Amiga+N, O, S, A, P, Q, X, C, V, Z).
  El resto, los habituales en ofimática (Amiga+B, I, U, F...).
- **Idioma:** los textos de la interfaz están en inglés en el código y se traducen con catálogos (`tr`, `@catalog` de
  Dash; decisión A11). En las tablas se dan los dos: inglés / español.
- **Una ventana por documento** (RF-N10). Cerrar la última ventana no cierra el programa si se abrió desde el
  Workbench sin documento: se deja una vacía. Propuesta; se decide en H5.
- **MUI recuerda** el tamaño y el sitio de cada ventana (id de ventana 1 para la principal).
- **Eventos:** los menús y objetos devuelven un número por `mui_wait_event`. Los números de Proyecto (1-11) y Edición
  (20-29) son los mismos en los dos programas, porque los atiende código común.

## 2. Lorraine Calc: ventana principal

```
┌ Lorraine Calc - presupuesto.ods ────────────────────────────────────────────────────┐
│ Project  Edit  View  Insert  Format  Data  Sheet  Settings                         │  menús
├────────────────────────────────────────────────────────────────────────────────────┤
│ [Nuevo][Abrir][Guardar] │ [Deshacer][Rehacer] │ [B][I][U] │ [≡◄][≡][►≡] │ [%][,0][Σ] │  barra de herramientas
├──────────┬─────────────────────────────────────────────────────────────────────────┤
│ B4       │ =SUMA(B1:B3)*2                                                           │  barra de fórmulas
├────┬─────┴─────┬───────────┬───────────┬───────────┬───────────┬──────────────┬───┤
│    │     A     │     B     │     C     │     D     │     E     │      F       │ ▲ │  cabecera de columnas
├────┼───────────┼───────────┼───────────┼───────────┼───────────┼──────────────┤   │
│  1 │ Concepto  │    120,00 │           │           │           │              │   │
│  2 │ Luz       │     45,50 │           │           │           │              │ █ │
│  3 │ Agua      │     30,25 │           │           │           │              │   │  rejilla (lienzo)
│  4 │ Total     │▐  391,50 ▌│           │           │           │              │   │
│  5 │           │           │           │           │           │              │   │
│  … │           │           │           │           │           │              │ ▼ │
├────┴───────────┴───────────┴───────────┴───────────┴───────────┴──────────────┴───┤
│ ◄ ►                                                                           ◄ █ ► │  barra horizontal
├────────────────────────────────────────────────────────────────────────────────────┤
│ [Hoja1][Gastos][Resumen] [+]                                                       │  pestañas de hojas
├────────────────────────────────────────────────────────────────────────────────────┤
│ Hoja 1 de 3   │ Suma=391,50  Promedio=195,75  Cuenta=2           │ Listo           │  barra de estado
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Objetos

| Nombre | Tipo MUI | Evento | Notas |
|---|---|---|---|
| `herramientas` | grupo horizontal de botones con imagen | 110-129 | Negrita, cursiva y subrayado se quedan pulsados según la celda activa **[D14]** |
| `ref` | campo de texto (32) | 102 al pulsar Return | Muestra la celda activa (`B4`) o el rango (`B1:B3`). Escribir una referencia o un nombre definido salta a él |
| `formula` | campo de texto (8192) | 103 al pulsar Return; 104 al cambiar | Contenido de la celda activa: la fórmula en el idioma del usuario, o el valor |
| `rejilla` | lienzo con doble búfer | 100 (clic, rueda, tecla); 101 (mover) | Cabeceras, celdas, selección, cursor de edición. Se pinta solo lo visible |
| `barra_v`, `barra_h` | barras de desplazamiento | 105, 106 | Rango: última fila o columna usada más una pantalla |
| `pestanas` | grupo de botones, o lienzo propio | 107 | Una pestaña por hoja; [+] crea una. Propuesta: lienzo propio, para poder arrastrar y renombrar con doble clic **[D12]** |
| `estado` | texto | — | Hoja, cálculos de la selección (RF-C23), modo (Listo, Editar, Apuntar) |

### 2.2 Menús de Calc

**Project / Proyecto**

| Opción (inglés / español) | Atajo | Evento | Qué hace |
|---|---|---|---|
| New / Nuevo | Amiga+N | 1 | Libro nuevo en otra ventana |
| Open... / Abrir... | Amiga+O | 2 | Diálogo de ficheros (filtro `#?.(ods|fods|xlsx|csv)`) |
| Open recent / Abrir reciente ▸ | — | 3 | Submenú con los últimos 8 (RF-N11) **[D13]** |
| Save / Guardar | Amiga+S | 4 | Guarda en su formato; si es nuevo, como Guardar como |
| Save as... / Guardar como... | Amiga+A | 5 | Diálogo con el formato (ods, fods, xlsx, csv) |
| Export PDF... / Exportar a PDF... | — | 6 | H9 |
| Print... / Imprimir... | Amiga+P | 7 | H10 |
| Properties... / Propiedades... | — | 8 | Título, autor, fechas (RF-N15) |
| Close / Cerrar | Amiga+K | 9 | Cierra la ventana; pregunta si hay cambios (RF-N07) |
| About... / Acerca de... | Amiga+? | 10 | Ventana Acerca de |
| Quit / Salir | Amiga+Q | 11 | Cierra todas las ventanas, preguntando por cada una con cambios |

**Edit / Edición**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Undo / Deshacer | Amiga+Z | 20 | RF-N08 |
| Redo / Rehacer | Amiga+Y | 21 | RF-N08 |
| Cut / Cortar | Amiga+X | 22 | RF-N09 **[D18]** |
| Copy / Copiar | Amiga+C | 23 | RF-N09 **[D18]** |
| Paste / Pegar | Amiga+V | 24 | RF-N09 **[D18]** |
| Paste special... / Pegado especial... | — | 25 | Solo valores, solo formato, trasponer |
| Clear / Borrar | — (Supr) | 26 | Borra el contenido de la selección |
| Select all / Seleccionar todo | Amiga+L | 27 | Toda la hoja. Amiga+A es Guardar como en la guía de estilo; propuesta |
| Find & replace... / Buscar y reemplazar... | Amiga+F | 28 | RF-C19 |
| Find next / Buscar siguiente | Amiga+G | 29 | Repite la última búsqueda |
| Go to... / Ir a... | Amiga+J | 30 | Pide una referencia o un nombre |

**View / Ver**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Grid / Cuadrícula ✓ | — | 40 | Muestra u oculta las líneas **[D13]** |
| Headers / Cabeceras ✓ | — | 41 | **[D13]** |
| Formula bar / Barra de fórmulas ✓ | — | 42 | **[D13]** |
| Show formulas / Ver fórmulas ✓ | Amiga+` | 43 | Las celdas muestran la fórmula, no el valor **[D13]** |
| Zoom ▸ 50 % / 75 % / 100 % / 150 % / 200 % | — | 44-48 | **[D13]** |
| Freeze panes / Inmovilizar ✓ | — | 49 | En la celda activa (RF-C20) |

**Insert / Insertar**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Rows / Filas | — | 50 | Tantas como filas seleccionadas, encima (RF-C16) |
| Columns / Columnas | — | 51 | A la izquierda |
| Cells... / Celdas... | — | 52 | Desplazando hacia abajo o a la derecha |
| Sheet / Hoja | — | 53 | Hoja nueva después de la actual |
| Function... / Función... | — | 54 | Lista de funciones por grupo, con su ayuda en una línea |
| Name... / Nombre... | — | 55 | Nombre definido para la selección (RF-C21) |

**Format / Formato**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Cells... / Celdas... | Amiga+1 | 60 | Ventana de formato de celda (§ 4.1) |
| Bold / Negrita | Amiga+B | 61 | RF-C13 |
| Italic / Cursiva | Amiga+I | 62 | |
| Underline / Subrayado | Amiga+U | 63 | |
| Number format ▸ General / 0,00 / 1.234,00 / % / € / Date / Time | — | 64-70 | Atajo a los formatos más usados **[D13]** |
| Column width... / Ancho de columna... | — | 71 | RF-C14 |
| Optimal width / Ancho óptimo | — | 72 | |
| Row height... / Alto de fila... | — | 73 | |
| Hide / Ocultar | — | 74 | Filas o columnas seleccionadas |
| Show / Mostrar | — | 75 | |
| Merge cells / Combinar celdas ✓ | — | 76 | RF-C15 **[D13]** |

**Data / Datos**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Sort... / Ordenar... | — | 80 | RF-C18 **[D7, D8]** |
| Fill down / Rellenar hacia abajo | Amiga+D | 81 | RF-C17 |
| Fill right / Rellenar a la derecha | Amiga+R | 82 | |
| Series... / Series... | — | 83 | |
| AutoSum / Autosuma | Amiga+= | 84 | RF-C22 |
| Recalculate all / Recalcular todo | — | 85 | Recalcula el libro entero, también lo que se abrió con valores guardados (A8) |

**Sheet / Hoja**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Rename... / Cambiar nombre... | — | 90 | RF-C05 |
| Delete / Borrar | — | 91 | Pregunta antes |
| Move left / Mover a la izquierda | — | 92 | |
| Move right / Mover a la derecha | — | 93 | |
| Next sheet / Hoja siguiente | Amiga+. | 94 | |
| Previous sheet / Hoja anterior | Amiga+, | 95 | |

**Settings / Preferencias**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Preferences... / Preferencias... | — | 96 | § 4.4 |
| MUI... | — | 97 | Preferencias de MUI del programa |

### 2.3 Eventos de Calc que no son menús

| Constante | Valor | Origen | Qué hace |
|---|---|---|---|
| `ID_REJILLA` | 100 | `mui_canvas_on_input` | Clic, rueda o tecla sobre la rejilla |
| `ID_MOVER` | 101 | `mui_canvas_on_move` y arrastre **[D12]** | Seleccionar arrastrando, cambiar el ancho de una columna |
| `ID_REF` | 102 | Return en `ref` | Saltar a la referencia |
| `ID_FORMULA` | 103 | Return en `formula` | Confirmar la edición |
| `ID_FORMULA_CAMBIA` | 104 | cambio en `formula` | Repintar la celda mientras se escribe |
| `ID_BARRA_V`, `ID_BARRA_H` | 105, 106 | barras | Desplazar |
| `ID_PESTANA` | 107 | pestañas | Cambiar de hoja |
| `ID_TIC` | 108 | `mui_timer` | Parpadeo del cursor de edición, desplazamiento al arrastrar fuera del borde |
| `ID_CERRADA + k` | 200 + k | cierre de la ventana k | Como Cerrar |
| Botones de la barra | 110-129 | `mui_on_press` | Los mismos que su opción de menú |

### 2.4 Teclado en la rejilla

Los teclados clásicos del Amiga no tienen Inicio, Fin, RePág ni AvPág. Se dan atajos con Alt para todo, y además
esas teclas si el teclado las tiene (teclado de PC por USB, emulador). Los códigos de esas teclas están **sin
comprobar**.

| Tecla | Sin editar | Editando una celda |
|---|---|---|
| Flechas | Mueven la celda activa | Mueven el cursor en el texto (izquierda y derecha); arriba y abajo confirman y se mueven |
| Shift + flechas | Amplían la selección **[D11]** | Seleccionan texto **[D11]** |
| Ctrl + flechas | Saltan al borde del bloque de datos **[D11]** | Saltan por palabras **[D11]** |
| Alt + arriba / abajo | Una pantalla arriba o abajo **[D11]** | — |
| Alt + izquierda / derecha | Columna A / última columna usada **[D11]** | Inicio / fin del texto **[D11]** |
| Return | Baja una celda | Confirma y baja |
| Shift + Return | Sube una celda | Confirma y sube |
| Tab / Shift + Tab | Derecha / izquierda | Confirma y se mueve |
| Esc | Quita la selección de copiar | Cancela la edición |
| F2 | Edita la celda activa con su contenido | — |
| Supr | Borra el contenido de la selección | Borra el carácter a la derecha |
| Retroceso | Borra la celda y empieza a editar | Borra el carácter a la izquierda |
| Un carácter | Empieza a editar con ese carácter (`mui_canvas_char`) | Lo escribe |
| F9 | Recalcula todo | — |

Edición: se escribe **dentro de la celda**, dibujado en el lienzo, y a la vez se ve en `formula`. Con una fórmula a
medio escribir, las flechas y el clic **apuntan** una referencia (modo Apuntar), como en LibreOffice. El editor de una
línea dentro del lienzo es el mismo código que usa Write (`core/`), propuesta a confirmar en H3.

### 2.5 Ratón en la rejilla

| Acción | Qué hace |
|---|---|
| Clic | Celda activa |
| Shift + clic | Amplía la selección hasta ahí **[D11]** |
| Arrastrar | Selecciona un rango **[D12]** |
| Clic en una cabecera | Fila o columna entera; arrastrando, varias **[D12]** |
| Arrastrar el borde de una cabecera | Cambia el ancho o el alto; el puntero cambia de forma **[D12, D16]** |
| Doble clic en el borde de una cabecera | Ancho o alto óptimo |
| Doble clic en una celda | Edita |
| Rueda | Desplaza 3 filas; con Shift, columnas **[D11]** |
| Botón derecho | Menú contextual: cortar, copiar, pegar, insertar, borrar, formato **[D15]** |

## 3. Lorraine Write: ventana principal

```
┌ Lorraine Write - carta.odt ────────────────────────────────────────────────────────┐
│ Project  Edit  View  Insert  Format  Table  Tools  Settings                        │  menús
├────────────────────────────────────────────────────────────────────────────────────┤
│ [Nuevo][Abrir][Guardar] │ [Deshacer][Rehacer] │ [Buscar]                             │  barra de herramientas
├────────────────────────────────────────────────────────────────────────────────────┤
│ [Cuerpo de texto ▼] [Liberation Serif ▼] [12 ▼] │ [B][I][U] │ [≡◄][≡][►≡][≡≡] │ [•][1.] │  barra de formato
├────────────────────────────────────────────────────────────────────────────────────┤
│   ·  1  ·  ·  2  ·  ·  3  ·  ·  4  ·  ·  5  ·  ·  6  ·  ·  7  ·  ·  8  ·  ·  ▼ ·    │  regla
├────────────────────────────────────────────────────────────────────────────────┬───┤
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ▲ │
│ ░░░░ ┌──────────────────────────────────────────────────────────────┐ ░░░░░░░ │   │
│ ░░░░ │                                                              │ ░░░░░░░ │   │
│ ░░░░ │   Estimada Sra. García:                                      │ ░░░░░░░ │ █ │  páginas (lienzo)
│ ░░░░ │                                                              │ ░░░░░░░ │   │
│ ░░░░ │   Le escribo para confirmarle que el pedido salió ayer|      │ ░░░░░░░ │   │
│ ░░░░ │   desde Málaga y llegará el lunes.                           │ ░░░░░░░ │   │
│ ░░░░ │                                                              │ ░░░░░░░ │ ▼ │
├────┴─┴──────────────────────────────────────────────────────────────┴─────────┴───┤
│ Página 1 de 3  │ 245 palabras  │ Español  │ INS  │ 100 %                            │  barra de estado
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Objetos

| Nombre | Tipo MUI | Evento | Notas |
|---|---|---|---|
| `herramientas` | botones con imagen | 110-119 | Igual que en Calc |
| `estilo` | desplegable con los estilos de párrafo del documento | 120 | La lista cambia con el documento **[D14]** |
| `fuente` | desplegable con las fuentes | 121 | **[D14]**; en H8, también TrueType |
| `tamano` | desplegable editable (8-72) | 122 | **[D14]** |
| `formato` | botones que se quedan pulsados: B, I, U, alineación, viñetas, numeración | 123-131 | Reflejan el formato en el cursor **[D14]** |
| `regla` | lienzo | 132 | Sangrías y tabulaciones del párrafo; arrastrables **[D12]**. Propuesta para H7; en H6 solo se ve |
| `paginas` | lienzo con doble búfer | 100 (clic, rueda, tecla); 101 (mover) | Páginas visibles con su zoom; cursor y selección |
| `barra_v` | barra de desplazamiento vertical | 105 | En twips escalados al zoom |
| `barra_h` | barra horizontal | 106 | Solo si la página no cabe a lo ancho |
| `estado` | texto | — | Página, palabras (RF-W16), idioma, inserción o sobrescritura, zoom |

### 3.2 Menús de Write

**Project** y **Edit** como en Calc (eventos 1-11 y 20-30), con el filtro de ficheros `#?.(odt|fodt|docx|txt)` y los
formatos odt, fodt, docx y txt en Guardar como. Edición › Seleccionar todo selecciona el documento entero.

**View / Ver**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Ruler / Regla ✓ | — | 40 | **[D13]** |
| Formatting marks / Marcas de formato ✓ | Amiga+* | 41 | Espacios, tabulaciones y finales de párrafo visibles **[D13]** |
| Zoom ▸ Whole page / Page width / 50 % / 75 % / 100 % / 150 % / 200 % | — | 42-48 | RF-W04 **[D13]** |

**Insert / Insertar**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Page break / Salto de página | Ctrl+Return | 50 | RF-W10 |
| Image... / Imagen... | — | 51 | RF-W13 (H8) |
| Table... / Tabla... | — | 52 | Filas y columnas (H8) |
| Special character... / Carácter especial... | — | 53 | Tabla de caracteres de la fuente |
| Page number / Número de página | — | 54 | Campo, en cabecera o pie (H8) |
| Header / Cabecera ✓ | — | 55 | RF-W14 **[D13]** |
| Footer / Pie ✓ | — | 56 | **[D13]** |

**Format / Formato**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Character... / Carácter... | — | 60 | Ventana de carácter (fuente, tamaño, efectos, color) RF-W06 |
| Paragraph... / Párrafo... | — | 61 | Sangrías, espacios, interlineado, alineación, tabulaciones RF-W07 |
| Bold / Negrita | Amiga+B | 62 | |
| Italic / Cursiva | Amiga+I | 63 | |
| Underline / Subrayado | Amiga+U | 64 | |
| Align ▸ Left / Center / Right / Justify | Amiga+[ / Amiga+E / Amiga+] / Amiga+J | 65-68 | En Write, Amiga+J justifica (no hay "Ir a") |
| Bullets / Viñetas ✓ | — | 69 | RF-W11 (H8) **[D13]** |
| Numbering / Numeración ✓ | — | 70 | (H8) **[D13]** |
| Styles... / Estilos... | Amiga+T | 71 | Lista de estilos: aplicar, crear desde la selección, modificar RF-W08 |
| Page... / Página... | — | 72 | Tamaño, orientación, márgenes RF-W15 |

**Table / Tabla** (H8)

| Opción | Evento | Qué hace |
|---|---|---|
| Insert row above / below — Insertar fila encima / debajo | 80, 81 | RF-W12 |
| Insert column left / right — Insertar columna izquierda / derecha | 82, 83 | |
| Delete row / column / table — Borrar fila / columna / tabla | 84-86 | |
| Borders... / Bordes... | 87 | |

**Tools / Herramientas**

| Opción | Atajo | Evento | Qué hace |
|---|---|---|---|
| Word count / Contar palabras | — | 90 | Palabras y caracteres, del documento y de la selección (RF-W16) |

**Settings / Preferencias**: como en Calc (96, 97).

### 3.3 Teclado en el texto

| Tecla | Qué hace |
|---|---|
| Flechas | Carácter (por punto de código UTF-8, **[D5]**) o línea |
| Ctrl + izquierda / derecha | Palabra **[D11]** |
| Ctrl + arriba / abajo | Párrafo **[D11]** |
| Alt + izquierda / derecha | Inicio / fin de la línea **[D11]** |
| Alt + arriba / abajo | Una pantalla **[D11]** |
| Ctrl + Alt + arriba / abajo | Inicio / fin del documento **[D11]** |
| Shift + cualquiera de las anteriores | Selecciona **[D11]** |
| Return | Párrafo nuevo |
| Shift + Return | Salto de línea |
| Ctrl + Return | Salto de página |
| Tab | Tabulación; en una tabla, celda siguiente |
| Retroceso / Supr | Borra a la izquierda / derecha; con selección, la selección |
| Un carácter | Lo escribe (`mui_canvas_char`, de Latin-1 a UTF-8 **[D5]**) |
| Insert (si existe) | Inserción o sobrescritura |

Las teclas Inicio, Fin, RePág y AvPág también, si el teclado las tiene (sin comprobar, como en Calc).

### 3.4 Ratón en el texto

| Acción | Qué hace |
|---|---|
| Clic | Pone el cursor |
| Shift + clic | Selecciona hasta ahí **[D11]** |
| Arrastrar | Selecciona **[D12]** |
| Doble clic | Selecciona la palabra (dos clics en menos del tiempo de doble clic del sistema, medido con `time_ms`) |
| Triple clic | Selecciona el párrafo |
| Rueda | Desplaza |
| Botón derecho | Menú contextual: cortar, copiar, pegar, carácter, párrafo **[D15]** |
| Sobre el texto | Puntero en forma de I **[D16]** |

El cursor parpadea con `mui_timer` (`ID_TIC`, 108), cada 500 ms, repintando solo su rectángulo
(`mui_canvas_update_area`).

## 4. Ventanas secundarias

Todas son ventanas MUI de `core/interfaz` o del programa, con Aceptar y Cancelar. Esc cancela, Return acepta.

### 4.1 Formato de celda (Calc)

```
┌ Format cells / Formato de celda ─────────────────────────────────┐
│ [Number][Font][Alignment][Borders][Background]                    │  pestañas (mui_register_begin)
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ Category    [Number      ▼]                                    │ │
│ │ Decimals    [2  ]   [x] Thousands separator                   │ │
│ │ Negative    [-1.234,00 ▼]                                      │ │
│ │ Format code [#.##0,00                                    ]     │ │
│ │ Preview     1.234,57                                           │ │
│ └───────────────────────────────────────────────────────────────┘ │
│                                       [ Cancel ]  [   OK   ]      │
└──────────────────────────────────────────────────────────────────┘
```

| Pestaña | Contenido | Falta en Dash |
|---|---|---|
| Number / Número | Categoría, decimales, miles, negativos, código de formato, vista previa | — |
| Font / Fuente | Fuente, estilo, tamaño, color, subrayado, tachado | Elegir fuente **[D nueva: selector de fuente]**; color **[D nueva: selector de color]** |
| Alignment / Alineación | Horizontal, vertical, ajustar texto, sangría | — |
| Borders / Bordes | Qué lados, estilo de línea, color | Dibujo de muestra en un lienzo (existe); color **[D nueva: selector de color]** |
| Background / Fondo | Color de fondo | **[D nueva: selector de color]** |

### 4.2 Buscar y reemplazar (los dos)

```
┌ Find & replace / Buscar y reemplazar ────────────────────────────┐
│ Find     [Málaga                                           ]     │
│ Replace  [Malaga                                           ]     │
│ [x] Match case   [ ] Whole words   [ ] Formulas (Calc)          │
│ Search in [Sheet ▼]  (Calc: hoja / libro)                        │
│ [Find next] [Replace] [Replace all]                [ Close ]     │
└──────────────────────────────────────────────────────────────────┘
```

No es modal: se puede seguir editando con ella abierta. "Reemplazar todo" es un solo paso de deshacer.

### 4.3 Opciones de CSV (Calc, al abrir y al guardar)

```
┌ CSV options / Opciones de CSV ───────────────────────────────────┐
│ Character set [UTF-8         ▼]   (UTF-8, ISO-8859-1, Windows-1252)│
│ Separator     [Semicolon     ▼]   (coma, punto y coma, tabulador,  │
│                                    espacio, otro: [ ])             │
│ Text quote    ["             ▼]                                    │
│ [x] First row is header (solo al abrir)                            │
│ [x] Detect numbers and dates (solo al abrir)                       │
│ Preview                                                            │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Concepto | Importe | Fecha                                    │ │
│ │ Luz      | 45,50   | 24/10/2026                               │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                       [ Cancel ]  [   OK   ]      │
└──────────────────────────────────────────────────────────────────┘
```

La vista previa es una lista de MUI con las 10 primeras filas (`mui_list`).

### 4.4 Preferencias (las dos, con pestañas comunes y propias)

| Pestaña | Opciones |
|---|---|
| General | Formato de guardado por omisión (ODF u OOXML); número de documentos recientes; avisar al guardar en un formato con pérdidas |
| Language / Idioma | Separador decimal y de miles: los del sistema **[D19]** o a mano; idioma de los nombres de funciones (Calc) |
| Calc | Fuente y tamaño por omisión; recálculo automático o a mano; mover tras Return (abajo, derecha) |
| Write | Fuente y tamaño por omisión; tamaño de página por omisión (A4, Carta); unidad de la regla (cm, pulgadas) |
| Fonts / Fuentes | Tabla de sustitución: fuente del documento → fuente del Amiga (H6); carpeta de TrueType (H8) |

Se guardan en `ENVARC:Lorraine/` y `ENV:Lorraine/` (propuesta: un fichero de texto por programa).

### 4.5 Otras

Propiedades del documento (RF-N15), Ordenar (RF-C18), Series (RF-C17), Cambiar nombre de hoja, Ancho de columna, Alto
de fila, Insertar función, Carácter y Párrafo (Write), Página (Write), Insertar tabla, Acerca de. Se diseñan en su
hito.

## 5. Avisos y preguntas

Ventanas de aviso con `core/interfaz` (requester de MUI). Texto base en inglés / español. *Cursiva*: lo que se
rellena.

| ID | Cuándo | Texto (inglés / español) | Botones |
|---|---|---|---|
| M-01 | Cerrar con cambios (RF-N07) | Save changes to "*nombre*" before closing? / ¿Guardar los cambios de "*nombre*" antes de cerrar? | Save / Guardar · Don't save / No guardar · Cancel / Cancelar |
| M-02 | Fichero dañado (RF-N03) | "*nombre*" is damaged and cannot be opened. / "*nombre*" está dañado y no se puede abrir. | OK / Aceptar |
| M-03 | Fichero cifrado (RF-N03) | "*nombre*" is protected with a password. Lorraine cannot open encrypted documents yet. / "*nombre*" está protegido con contraseña. Lorraine aún no abre documentos cifrados. | OK / Aceptar |
| M-04 | Formato desconocido (RF-N03) | Lorraine does not know the format of "*nombre*". / Lorraine no conoce el formato de "*nombre*". | OK / Aceptar |
| M-05 | Formato antiguo (`.xls`, `.doc`) | "*nombre*" is an old Office file (.xls/.doc). Save it as .xlsx/.docx or .ods/.odt on the PC first. / "*nombre*" es un fichero antiguo de Office (.xls/.doc). Guárdalo antes en el PC como .xlsx/.docx u .ods/.odt. | OK / Aceptar |
| M-06 | Sin memoria (RNF-04) | Not enough memory to *acción*. Close other documents or programs and try again. / No hay memoria suficiente para *acción*. Cierra otros documentos o programas y vuelve a intentarlo. | OK / Aceptar |
| M-07 | Guardar con pérdidas (RF-N06) | This document had things Lorraine does not keep: *lista*. If you save it as *formato*, they will be lost. / Este documento tenía cosas que Lorraine no conserva: *lista*. Si lo guardas como *formato*, se perderán. | Save / Guardar · Save as... / Guardar como... · Cancel / Cancelar |
| M-08 | No se pudo guardar (disco lleno, protegido) | Could not save "*nombre*": *motivo*. The original file has not been changed. / No se pudo guardar "*nombre*": *motivo*. El fichero original no ha cambiado. | OK / Aceptar |
| M-09 | Función que Lorraine no tiene (RF-C11), al editar esa celda | This formula uses *FUNCIÓN*, which Lorraine cannot calculate yet. The value shown is the one saved in the file. / Esta fórmula usa *FUNCIÓN*, que Lorraine aún no sabe calcular. El valor que se ve es el que traía el fichero. | OK / Aceptar |
| M-10 | Fórmula mal escrita | The formula has an error: *detalle*. / La fórmula tiene un error: *detalle*. | Fix / Corregir · Cancel / Cancelar |
| M-11 | Referencia circular (RF-C09) | Circular reference in *celda*. / Referencia circular en *celda*. | OK / Aceptar (y la celda muestra `Err:522`) |
| M-12 | Borrar una hoja | Delete sheet "*nombre*"? This can be undone. / ¿Borrar la hoja "*nombre*"? Se puede deshacer. | Delete / Borrar · Cancel / Cancelar |
| M-13 | Pegar sobre celdas con datos | Replace the contents of the destination cells? / ¿Sustituir el contenido de las celdas de destino? | Replace / Sustituir · Cancel / Cancelar |
| M-14 | Fichero abierto ya en otra ventana | "*nombre*" is already open. / "*nombre*" ya está abierto. | Show / Mostrar · Cancel / Cancelar |
| M-15 | Caracteres que no se ven (A3) | — | Sin aviso: se pintan como `?` y se conservan al guardar. Propuesta |

Mensajes de la barra de estado (sin ventana): "Opening *nombre*... / Abriendo *nombre*...", "Saving... / Guardando...",
"Recalculating... / Recalculando...", "Repaginating... / Repaginando..." (Write, cuando tarda más de 0,5 s).

## 6. Iconos

Iconos de la barra de herramientas en ILBM dentro de `PROGDIR:iconos/` (como Tachyon); iconos de Workbench para los
dos programas y para los tipos de documento (propuesta: uno por formato, para que el Workbench los distinga). Diseño
pendiente.

## 7. Accesibilidad y tamaños

- Todo lo que hace el ratón se puede hacer con el teclado y los menús.
- Los tamaños salen de la fuente de la pantalla (`screen_font_height`), no de píxeles fijos.
- La rejilla y las páginas funcionan en pantallas de 640x256 (PAL sin entrelazar): las barras se pueden ocultar desde
  Ver. Propuesta; se prueba en H2 y H6.

## 8. Lo que falta en Dash, encontrado al diseñar esta interfaz

Ya tienen número en [13](13_DASH.md): D25 a D30, en este orden.

| Qué | Para qué | Prio. propuesta | Hito |
|---|---|---|---|
| Poner el foco del teclado en un objeto MUI (`mui_set_active(obj)`) y saber cuál lo tiene | Pasar de la rejilla al campo de fórmula y volver; buscar y reemplazar | E | H3 |
| Selector de color (`Poppen` de MUI) | Formato de celda y de carácter | I | H4 |
| Selector de fuente (`Popasl` de MUI, o el de ASL) | Formato de celda y de carácter | I | H4 |
| Desplegable editable y con la lista cambiable desde el programa (estilos, tamaños) | Barra de formato de Write | I | H7 (puede entrar en D14) |
| Tiempo de doble clic del sistema (`DoubleClick()` de Intuition) | Doble y triple clic en Write y en la rejilla | D | H7 |
| Ventanas no modales además de la principal, con sus eventos | Buscar y reemplazar abierto mientras se edita | I | H5 |
