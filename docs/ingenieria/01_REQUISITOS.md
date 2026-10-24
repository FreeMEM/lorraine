# 01. Requisitos

Lo que tiene que hacer Lorraine y cómo se comprueba. Escrito antes de construir: todos los requisitos están
pendientes. El hito de cada uno es el de [11](11_PLAN_DE_CONSTRUCCION.md); las pruebas, las de
[08](08_PLAN_DE_PRUEBAS.md).

**Prioridad:** E (esencial: sin esto no hay programa), I (importante), D (deseable).

## 1. Alcance

Lorraine es una suite ofimática para AmigaOS 3.x con interfaz MUI, escrita en Dash, con licencia MIT. La forman
Lorraine Calc (hoja de cálculo) y Lorraine Write (procesador de textos). Los dos abren y guardan los formatos de
LibreOffice (ODF) y de Microsoft Office moderno (OOXML).

Fuera de alcance de la 1.0: lo de [ARQUITECTURA](../ARQUITECTURA.md) § 10 (macros, tablas dinámicas, gráficos,
formato condicional, control de cambios, comentarios, notas al pie, ecuaciones, objetos incrustados, documentos
cifrados, `.xls`, `.doc`, RTF).

## 2. Usuarios y entorno

- **Usuario:** alguien con un Amiga ampliado o un emulador que quiere hacer cuentas, cartas, informes, y abrir y
  devolver los ficheros que le llegan de un PC.
- **Entorno:** AmigaOS 3.1 o superior, MUI 3.8 o 5, 68020 o mejor con FPU. Ver RNF-01.

## 3. Requisitos funcionales

### 3.1 Comunes a los dos programas (RF-N)

| ID | Requisito | Criterio de aceptación | Prio. | Hito |
|---|---|---|---|---|
| RF-N01 | Abrir un documento desde el diálogo de ficheros o como argumento (Shell y icono del Workbench). | Abre los ficheros del corpus por las tres vías. | E | H2 |
| RF-N02 | Reconocer el formato por el contenido, no por la extensión. | Un `.xlsx` renombrado a `.ods` se abre como xlsx. | I | H1 |
| RF-N03 | Avisar con un mensaje claro si el fichero no se puede abrir (dañado, cifrado, formato desconocido, sin memoria). | Cada caso del corpus de ficheros malos da su mensaje, sin colgarse ni perder memoria. | E | H2 |
| RF-N04 | Guardar y Guardar como, eligiendo el formato. | Guarda en cada formato de su programa. | E | H3 |
| RF-N05 | Guardar de forma segura: a un temporal y luego se cambia por el original. | Un fallo simulado a mitad deja el original intacto. | E | H3 |
| RF-N06 | Avisar al guardar en el formato original si al abrir se perdió algo (decisión A9), diciendo qué. | El corpus con gráficos o macros da el aviso con la lista. | I | H3 |
| RF-N07 | Preguntar antes de cerrar un documento con cambios sin guardar. | Cerrar con cambios pregunta; sin cambios, no. | E | H3 |
| RF-N08 | Deshacer y rehacer cualquier cambio del documento, al menos 100 pasos. | Cada orden de edición se deshace y rehace dejando el documento igual. | E | H3 / H7 |
| RF-N09 | Copiar, cortar y pegar, también con otros programas del Amiga (texto) y entre Calc y Write. | Pegar en Calc un texto con tabuladores lo reparte en celdas; pegar celdas en Write da texto. | I | H5 / H7 |
| RF-N10 | Varios documentos abiertos, cada uno en su ventana. | Dos libros abiertos a la vez, cada uno con sus cambios. | I | H5 / H7 |
| RF-N11 | Documentos recientes en el menú. | Los últimos 8 abiertos, guardados entre sesiones. | D | H5 |
| RF-N12 | Exportar a PDF. | Ver H9. | I | H9 |
| RF-N13 | Imprimir. | Ver H10. | D | H10 |
| RF-N14 | Interfaz en inglés y español con catálogos. | Con el idioma del sistema en español, los menús salen en español. | I | H5 |
| RF-N15 | Propiedades del documento: título, autor, fechas. Se leen y se guardan. | Se conservan al abrir y guardar en el mismo formato. | D | H5 |
| RF-N16 | Abrir un documento soltando su icono en la ventana. | Soltar un `.ods` en Calc lo abre en una ventana nueva. | D | H5 |

### 3.2 Lorraine Calc (RF-C)

| ID | Requisito | Criterio de aceptación | Prio. | Hito |
|---|---|---|---|---|
| RF-C01 | Abrir `.ods`, `.fods`, `.xlsx` y `.csv`. | Valores iguales al volcado de LibreOffice para todo el corpus. | E | H2 |
| RF-C02 | Guardar `.ods` y `.fods`. | LibreOffice lo abre con los mismos valores y fórmulas; pasa el validador de ODF. | E | H3 |
| RF-C03 | Guardar `.xlsx`. | LibreOffice lo abre igual; pasa la validación de OOXML; muestra revisada en Excel. | E | H4 |
| RF-C04 | Guardar `.csv` eligiendo separador, comillas y juego de caracteres. | Lo lee LibreOffice con esas opciones. | I | H4 |
| RF-C05 | Varias hojas por libro: crear, borrar, renombrar, mover, cambiar de una a otra. | Las operaciones se guardan y se deshacen. | E | H2 (ver) / H5 |
| RF-C06 | Escribir en una celda: número, texto, fecha, porcentaje, lógico o fórmula, reconociendo cada uno al escribirlo según el idioma. | `1.234,5`, `25%`, `24/10/2026`, `VERDADERO` y `=A1*2` quedan como su tipo en español. | E | H3 |
| RF-C07 | Moverse y seleccionar con teclado y ratón: flechas, Shift, Ctrl, re pág, inicio, clic, arrastrar, filas y columnas enteras. | Cada combinación selecciona lo esperado. | E | H3 |
| RF-C08 | Fórmulas con referencias relativas, absolutas y mixtas, rangos, referencias a otras hojas y nombres definidos. | Las fórmulas del corpus dan lo mismo que en LibreOffice. | E | H3 |
| RF-C09 | Recalcular solo lo que depende de lo que cambió; detectar referencias circulares. | Cambiar una celda recalcula sus dependientes y nada más (contador de prueba). Un círculo da `Err:522`. | E | H3 |
| RF-C10 | Las funciones de § 3.3. | Cada función con sus tests, contra los valores de LibreOffice. | E | H3 / H5 |
| RF-C11 | Si un libro usa una función que Lorraine no tiene, mostrar el valor guardado y avisar en esa celda. | La celda muestra el valor y una marca; al editarla, un aviso. | I | H2 |
| RF-C12 | Formatos de número: general, decimales, miles, moneda, porcentaje, científico, fecha, hora, texto y códigos a medida. | Los formatos del corpus se ven igual que en LibreOffice. | E | H2 / H4 |
| RF-C13 | Formato de celda: fuente, tamaño, negrita, cursiva, subrayado, color, fondo, bordes, alineación horizontal y vertical, ajustar texto. | Se ve, se guarda y se conserva en los dos formatos. | E | H4 |
| RF-C14 | Ancho de columnas y alto de filas, a mano y automático; ocultar filas y columnas. | Se ve y se conserva. | E | H4 |
| RF-C15 | Combinar celdas. | Se ve y se conserva. | I | H4 |
| RF-C16 | Insertar y borrar filas, columnas y celdas, ajustando las referencias de las fórmulas. | Las fórmulas siguen apuntando a los mismos datos. | E | H5 |
| RF-C17 | Rellenar: copiar hacia abajo o la derecha y series (1, 2, 3...; enero, febrero...; fechas), desde el menú y arrastrando el tirador de la esquina de la selección. | Las series del caso de uso dan lo esperado por las dos vías. | I | H5 |
| RF-C18 | Ordenar un rango por una o varias columnas, ascendente o descendente. | Igual que LibreOffice con los mismos datos. | I | H5 |
| RF-C19 | Buscar y reemplazar en valores y fórmulas. | Encuentra todas las apariciones. | I | H5 |
| RF-C20 | Inmovilizar filas y columnas. | Se ve y se conserva. | I | H5 |
| RF-C21 | Nombres definidos: crear, usar en fórmulas, borrar. | Se conservan en los dos formatos. | I | H5 |
| RF-C22 | Autosuma: con una tecla, la suma del bloque de encima o de la izquierda. | Propone el rango correcto. | D | H5 |
| RF-C23 | Barra de estado con la suma, el promedio y la cuenta de la selección. | Valores correctos al seleccionar. | D | H5 |
| RF-C24 | Al escribir una fórmula, una tecla (F4) cambia la referencia bajo el cursor entre relativa, absoluta y mixta. | `A1` → `$A$1` → `A$1` → `$A1` → `A1`. | I | H3 |
| RF-C25 | Los errores de celda se muestran en el idioma del usuario (`#¡DIV/0!` en español) y se guardan con el código de cada formato ([12](12_FORMATOS.md) § 3.7). | Un error del corpus se ve traducido y se guarda igual que estaba. | I | H3 |

Fuera de la 1.0: seleccionar varias zonas sueltas a la vez (Ctrl+clic).

### 3.3 Funciones de Calc

Con su nombre inglés (el de los ficheros). En español se muestran traducidas (`SUM` → `SUMA`). **H3:** el primer
grupo. **H5:** el segundo.

| Grupo | H3 | H5 |
|---|---|---|
| Matemáticas | SUM, PRODUCT, ABS, ROUND, ROUNDUP, ROUNDDOWN, INT, MOD, POWER, SQRT, PI, SIGN, TRUNC | SUMIF, SUMIFS, SUMPRODUCT, CEILING, FLOOR, EXP, LN, LOG, LOG10, FACT, GCD, LCM, RAND, RANDBETWEEN, SIN, COS, TAN, ASIN, ACOS, ATAN, ATAN2, DEGREES, RADIANS, EVEN, ODD, MROUND, QUOTIENT, SUBTOTAL |
| Estadística | AVERAGE, COUNT, COUNTA, COUNTBLANK, MAX, MIN | AVERAGEIF, AVERAGEIFS, COUNTIF, COUNTIFS, MEDIAN, MODE, LARGE, SMALL, RANK, STDEV, STDEVP, VAR, VARP, PERCENTILE, QUARTILE |
| Lógica | IF, AND, OR, NOT, TRUE, FALSE, IFERROR | IFNA, XOR, IFS, SWITCH |
| Texto | CONCATENATE, LEFT, RIGHT, MID, LEN, UPPER, LOWER, TRIM, TEXT, VALUE | FIND, SEARCH, SUBSTITUTE, REPLACE, REPT, PROPER, EXACT, CHAR, CODE, TEXTJOIN, CONCAT, FIXED, DOLLAR |
| Fecha y hora | DATE, TODAY, NOW, YEAR, MONTH, DAY | TIME, HOUR, MINUTE, SECOND, WEEKDAY, WEEKNUM, EDATE, EOMONTH, DATEDIF, DAYS, NETWORKDAYS, WORKDAY, DATEVALUE, TIMEVALUE |
| Búsqueda | VLOOKUP, HLOOKUP, INDEX, MATCH | LOOKUP, CHOOSE, ROW, COLUMN, ROWS, COLUMNS, OFFSET, INDIRECT, ADDRESS, XLOOKUP |
| Información | ISBLANK, ISNUMBER, ISTEXT, ISERROR | ISNA, ISLOGICAL, ISEVEN, ISODD, NA, TYPE, N |
| Financieras | — | PMT, FV, PV, NPV, IRR, RATE, NPER |

Unas 150 en total. Excel tiene unas 500: el resto se apunta a medida que aparezcan en ficheros reales (RF-C11 cubre
mientras tanto).

### 3.4 Lorraine Write (RF-W)

| ID | Requisito | Criterio de aceptación | Prio. | Hito |
|---|---|---|---|---|
| RF-W01 | Abrir `.odt`, `.fodt`, `.docx` y `.txt`. | Texto, orden y formato de carácter iguales al volcado de LibreOffice para el corpus. | E | H6 |
| RF-W02 | Guardar `.odt`, `.fodt` y `.docx`. | LibreOffice lo abre igual; pasa los validadores. | E | H7 |
| RF-W03 | Guardar `.txt` (UTF-8 o Latin-1). | El texto sale entero, un párrafo por línea. | I | H7 |
| RF-W04 | Ver las páginas con su tamaño, márgenes y zoom (página entera, ancho, 50-200 %). | El corpus se ve paginado. | E | H6 |
| RF-W05 | Escribir, borrar, mover el cursor (carácter, palabra, línea, párrafo, página, inicio y fin) y seleccionar con teclado y ratón. | Cada tecla hace lo esperado; doble clic selecciona la palabra, triple el párrafo. | E | H7 |
| RF-W06 | Formato de carácter: fuente, tamaño, negrita, cursiva, subrayado, tachado, color, resaltado, superíndice, subíndice. | Se ve, se guarda y se conserva en los dos formatos. | E | H7 |
| RF-W07 | Formato de párrafo: alineación (también justificado), sangrías, espacio antes y después, interlineado, tabulaciones. | Se ve, se guarda y se conserva. | E | H7 |
| RF-W08 | Estilos de párrafo y de carácter con herencia: aplicar, y respetar los del documento. | Los estilos del corpus se conservan con su nombre. | E | H6 / H7 |
| RF-W09 | Buscar y reemplazar, distinguiendo mayúsculas o no, palabra entera o no. | Encuentra todas las apariciones. | I | H7 |
| RF-W10 | Saltos de página y de línea. | Se ven y se conservan. | E | H7 |
| RF-W11 | Listas con viñetas y numeradas, con niveles. | Se ven y se conservan en los dos formatos. | E | H8 |
| RF-W12 | Tablas: ver, editar texto, añadir y quitar filas y columnas, bordes, anchos. | Las tablas del corpus se ven y se conservan. | E | H8 |
| RF-W13 | Imágenes en línea con el texto (PNG, JPEG, GIF por datatypes). | Se ven y se conservan. | I | H8 |
| RF-W14 | Cabecera y pie de página, con número de página. | Se ven y se conservan. | I | H8 |
| RF-W15 | Secciones con distinto tamaño u orientación de página. | Se ven y se conservan. | D | H8 |
| RF-W16 | Contar palabras y caracteres. | Igual que LibreOffice en el corpus (±1 %). | D | H7 |
| RF-W17 | Fuentes TrueType además de las del Amiga. | Se ven a cualquier tamaño. | I | H8 |

## 4. Requisitos no funcionales

Las cifras son objetivos de diseño, sin medir. Se miden en la máquina mínima, un A1200 con 68030 y FPU (entorno
"a1200-030" de [08](08_PLAN_DE_PRUEBAS.md)), desde H2, y se ajustan con el usuario si no son razonables.

| ID | Requisito | Criterio | Prio. |
|---|---|---|---|
| RNF-01 | Funciona en AmigaOS 3.1 y 3.2, MUI 3.8 y 5, 68020 o mejor con FPU. Va bien en un A1200 con 68030 y FPU. | La batería de tests pasa en las configuraciones de FS-UAE con 3.1 y 3.2; las RNF de rendimiento se cumplen en "a1200-030". | E |
| RNF-02 | Cero memoria perdida. | Abrir, editar y cerrar cada documento del corpus con `--memcheck`: 0 objetos vivos. | E |
| RNF-03 | Nunca perder el documento del usuario: guardado seguro (RF-N05) y sin cuelgues ante ficheros malos. | El corpus de ficheros malos (truncados, ZIP roto, XML roto, enormes) no cuelga ni pierde memoria. | E |
| RNF-04 | Sin memoria suficiente, avisar y dejar el programa usable. | Prueba con poca memoria libre: aviso y el resto de documentos siguen abiertos. | E |
| RNF-05 | Interoperabilidad: lo que Lorraine guarda lo abre LibreOffice igual, y pasa los validadores de ODF y OOXML. | Prueba de ida y vuelta de todo el corpus en cada versión. | E |
| RNF-06 | Licencia MIT; nada en el repositorio que no se pueda redistribuir así. | Revisión de `third_party/` en cada versión. | E |
| RNF-07 | Código en Dash; C solo en `third_party/` y su pegamento. | Revisión en cada hito. | E |
| RNF-08 | Cobertura de las normas medida en cada versión: tests de funciones de LibreOffice que pasan, pruebas de ODFAutoTests que se conservan, errores de los validadores ([08](08_PLAN_DE_PRUEBAS.md) § 4.5). | Las cifras salen en las notas de cada versión y no bajan de una a otra. | I |
| RNF-C01 | Calc abre un libro de 20.000 celdas con 2.000 fórmulas en menos de 5 s. | Medida en H2 y en cada versión. | I |
| RNF-C02 | Calc recalcula tras cambiar una celda en menos de 0,2 s en ese libro (cadena de dependencias normal). | Medida en H3. | I |
| RNF-C03 | Calc gasta menos de 8 MB con ese libro abierto. | Medida en H2. | I |
| RNF-C04 | Desplazar la hoja va sin saltos (repinta en menos de 50 ms). | Medida en H2. | I |
| RNF-W01 | Write abre un documento de 50 páginas en menos de 5 s. | Medida en H6. | I |
| RNF-W02 | Escribir sin retraso: cada tecla se ve en menos de 50 ms, también al principio de un documento de 50 páginas. | Medida en H7. | E |
| RNF-W03 | Write gasta menos de 8 MB con ese documento abierto (sin imágenes). | Medida en H6. | I |
