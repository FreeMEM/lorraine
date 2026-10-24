# 13. Lo que hay que añadir a Dash

Lorraine existe también para hacer crecer Dash. Lo que le falte a Dash se añade a Dash, no se rodea con `@native`.
Esta es la lista de partida, sacada de comparar lo que Lorraine necesita con lo que Dash tiene el 2026-10-24
(`docs/BUILTINS.md` de `main`, 615 builtins).

En Dash se citan como "lorraine D<n>" (igual que Tachyon usa "dashweb D<n>"), para que no choquen con los números de
Tachyon.

**Prioridad:** E (esencial: bloquea un hito), I (importante), D (deseable). **Hito:** el primero que lo necesita (ver
[11](11_PLAN_DE_CONSTRUCCION.md)).

## 1. Cómo se pide y se hace

- Se trabaja en un worktree de Dash propio, `~/Projects/FreeMEMLang/.worktrees/lorraine`, rama `lorraine`, que sale de
  `main`. Lorraine compila con esa rama (`$DASH`).
- Cada tarea se pide con: el porqué (qué parte de Lorraine la necesita), cómo reproducir la falta, lo que se propone
  y un test de Dash que la compruebe.
- Lo hace la sesión que trabaja en Dash, no el loop de Lorraine. Mientras, Lorraine sigue con lo que no dependa de eso.
- La rama `lorraine` se fusiona en `main` de Dash de vez en cuando, igual que `dashweb`. **Riesgo:** dos ramas que
  tocan el compilador a la vez. Ver R-03 en [10](10_RIESGOS_Y_PENDIENTES.md).

## 2. Tareas

### Números

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D1 | **Tipo `Double`** (IEEE 754 de 64 bits): literales, operaciones, comparaciones, conversiones con `Int`, `Float` y `String`, campos de struct, parámetros y retorno. Con `--fpu`, la FPU; sin ella, coma flotante por software (fp-bit ya trae la de 64 bits). | Toda celda con número. Con 32 bits, `0,1 + 0,2` y los importes grandes salen mal. | E | H2 |
| D2 | **Listas de `Double`** (`[Double]`), y de paso las de `Float`, que hoy no se pueden hacer. | Rangos de valores para SUMA, PROMEDIO, MEDIANA... | E | H3 |
| D3 | **`Double` a texto, el más corto que vuelve al mismo número** (Ryu, el `d2s` que ya está en `third_party/ryu` de Tachyon) y **de texto a `Double`** exacto. Con un número de decimales fijo también. | Mostrar y guardar números sin `0,30000000000000004` ni pérdidas al guardar. | E | H2 |
| D4 | **Funciones matemáticas para `Double`**: `sqrt`, `pow`, `exp`, `log`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `floor`, `ceil`, `round`, `trunc`, `fmod`, `abs`, `is_nan`, `is_inf`. | Las funciones de la hoja. | E | H3 |

### Texto

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D5 | **UTF-8**: `utf8_next(s, i)`, `utf8_prev(s, i)`, `utf8_code(s, i)` (punto de código), `utf8_char(cp)`, `utf8_length(s)`, `utf8_to_latin1(s)` (lo que no existe, por algo parecido o `?`), `latin1_to_utf8(s)`. Lo que hace `lib/texto.dash` de Tachyon, como builtins. | El texto interno es UTF-8 (decisión A3). El cursor de Write se mueve por caracteres, no por bytes. | E | H1 |
| D6 | **Comprimir**: `inflate(buf, n, salida, max)`, `deflate(buf, n, salida, max, nivel)`, `crc32(buf, n, crc)`, con zlib dentro del runtime de Dash. Tachyon podría dejar de usar el inflate de stb. | Todos los ficheros ODF y OOXML son ZIP. | E | H1 |
| D7 | **Comparar textos para ordenar** según el idioma (`locale.library` `StrnCmp`), sin distinguir mayúsculas si se pide. | Ordenar filas, BUSCARV aproximado, la ordenación de la hoja. | I | H5 |

### Colecciones

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D8 | **Ordenar listas** con una función de comparación (`lista.sort(f)`), estable. | Ordenar filas, MEDIANA, K.ESIMO.MAYOR, ordenar estilos. | E | H3 |
| D9 | **Diccionarios con clave `Int`** (`{Int: T}`). | Índices de estilos, de textos compartidos al leer xlsx, del grafo de dependencias. Hoy solo hay clave `String`. | I | H2 |
| D10 | **Buscar en una lista ordenada** (`lista.bsearch(valor, f)`). | Filas y celdas por índice cuando la lista es dispersa compacta; BUSCARV aproximado. | D | H5 |

### Interfaz (MUI y lienzo)

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D11 | **Teclas modificadoras** en el lienzo: `mui_canvas_qualifiers(canvas)` (Shift, Ctrl, Alt, Amiga) de la última tecla o clic. | Shift + flechas para seleccionar, Ctrl + flechas para saltar. Sin esto no hay selección por teclado. | E | H3 |
| D12 | **Arrastrar con el ratón** en el lienzo: evento al mover con el botón pulsado y al soltarlo. | Seleccionar rangos y texto, cambiar el ancho de columna. | E | H3 |
| D13 | **Menús con marca** (casilla) y **submenús**; cambiar la marca y activar o desactivar una opción desde el programa. | Ver › Cuadrícula, Formato › Negrita, menús de "Abrir recientes". | I | H3 |
| D14 | **Barra de herramientas** con botones de imagen que se quedan pulsados (negrita, cursiva) y campos desplegables (fuente, tamaño). | La barra de formato de los dos programas. | I | H4 |
| D15 | **Menú contextual** sobre el lienzo (botón derecho). | Copiar, pegar, insertar fila... donde está el ratón. | D | H5 |
| D16 | **Forma del puntero** sobre el lienzo (flecha, I de texto, flechas de redimensionar). | Saber que se puede arrastrar el borde de una columna. | D | H5 |
| D17 | **Medir y, si se puede, reducir la cabecera de los structs** (la pregunta 27c de `docs/MEJORAS_LOOP.md` de Dash). | Un libro tiene decenas de miles de celdas: cada byte de cabecera cuenta. | I | H2 (medir), H5 |
| D25 | **Foco del teclado**: ponerlo en un objeto MUI (`mui_set_active(obj)`) y saber cuál lo tiene. | Pasar de la rejilla al campo de fórmula y volver; buscar y reemplazar. | E | H3 |
| D26 | **Selector de color** (Poppen de MUI). | Formato de celda y de carácter. | I | H4 |
| D27 | **Selector de fuente** (Popasl de MUI, o el de ASL). | Formato de celda y de carácter. | I | H4 |
| D28 | **Desplegable editable** con la lista cambiable desde el programa. Puede entrar en D14. | Estilos y tamaños en la barra de formato de Write. | I | H7 |
| D29 | **Ventanas no modales** además de la principal, con sus eventos. | Buscar y reemplazar abierto mientras se edita. | I | H5 |
| D30 | **Tiempo de doble clic del sistema** (`DoubleClick()` de Intuition). | Doble y triple clic en Write y en la rejilla. | D | H7 |

### Sistema

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D18 | **Portapapeles**: `clip_write_text(s)`, `clip_read_text()` con `clipboard.device` e IFF FTXT; y escribir o leer un bloque con un identificador IFF propio. | Copiar y pegar entre programas del Amiga y entre Calc y Write. | E | H5 |
| D19 | **Separadores y formatos del idioma**: `locale_decimal_point()`, `locale_group_separator()`, `locale_date_order()`. | En español se escribe `1.234,5`; en inglés, `1,234.5`. Afecta a escribir y a mostrar números. | I | H3 |
| D20 | **Fecha y hora como números**: año, mes, día, hora, minuto y segundo de ahora. Hoy solo hay `date_text(formato)`. | `AHORA()`, `HOY()`; la fecha de modificación de los documentos. | I | H3 |
| D21 | **Imprimir** con `printer.device`: abrir, enviar una página como mapa de bits, cerrar. | Imprimir sin pasar por PDF. | D | H10 |
| D22 | **Puerto ARexx** de la aplicación MUI con órdenes propias. | Automatizar: rellenar una hoja desde un script. | D | H11 |
| D31 | **Argumentos del Workbench**: los iconos de proyecto con los que se arrancó el programa (doble clic en un documento, Shift+clic en varios). Hoy `arg_count()` da 0 desde el Workbench. | Abrir un documento con doble clic en su icono (RF-N01). | E | H2 |
| D32 | **Recibir iconos arrastrados a la ventana** (AppWindow). | Abrir un documento soltándolo en la ventana (RF-N16). | D | H5 |
| D33 | **Comentario y bits de protección de un fichero**: leerlos y ponerlos. | El guardado seguro cambia el original por un temporal: tiene que conservarlos (RF-N05). | I | H3 |
| D34 | **Base64**: codificar y descodificar entre texto y búfer. | Imágenes dentro de `.fods` y `.fodt` ([12](12_FORMATOS.md) § 2.3). Sirve también a Tachyon (direcciones `data:`). | I | H6 |

### Fuentes

| ID | Qué | Por qué | Prio. | Hito |
|---|---|---|---|---|
| D23 | **Pasar `fuente_web` de Tachyon a la librería de Dash** (TrueType a fuente del Amiga con stb_truetype), con medidas de cada carácter a un tamaño dado en twips. | Write necesita fuentes escalables y medidas finas. Tachyon y Lorraine compartirían el mismo código. | I | H8 |
| D24 | **Pintar texto con suavizado** en pantallas RTG (TrueType a 8 bits de alfa). | Que el texto se lea bien en zoom pequeño. | D | H8 |

## 3. Lo que se comprueba antes de pedir

Algunas faltas pueden no serlo. Antes de pedirlas se mira en Dash:

- Si `file_print` y `file_write` ya escriben con búfer (si no, una tarea más: escritura con búfer).
- Si la concatenación de textos sirve para escribir un XML de varios MB sin copiar de más.
- Si las listas de structs de decenas de miles de elementos se recorren y crecen sin coste raro.

Lo que salga se añade a esta lista con su número.

## 4. Choques de nombres

Lo que Lorraine escriba en Dash mientras espera una tarea no puede usar el prefijo que tendrá el builtin. El módulo
provisional de UTF-8 se llama `u8_`, no `utf8_` (D5). `fx_` ya es de `Fixed`. Las funciones privadas (`_x`) también
llevan el prefijo de su módulo: en C chocarían entre módulos (problema conocido de Dash).
