# Arquitectura de Lorraine

Cómo se va a construir Lorraine por dentro. Escrito el 2026-10-24, antes de la primera línea de código: es el diseño
de partida. Cuando el código exista, este documento describe el código y las diferencias se anotan aquí.

Qué es cada documento:

- **Este:** piezas, datos, procesos, decisiones con su porqué y límites.
- `ingenieria/`: el paquete de ingeniería completo. Empieza en `ingenieria/00_INDICE.md`.
- `ingenieria/13_DASH.md`: lo que hay que añadir a Dash (tareas `D<n>`).

Se actualiza cuando cambia la arquitectura, no en cada tarea.

## 1. Objetivo y restricciones

Lorraine es una suite ofimática libre (MIT) para AmigaOS 3.x con interfaz MUI. Tiene dos programas:

- **Lorraine Calc:** hoja de cálculo.
- **Lorraine Write:** procesador de textos.

Los dos abren y guardan los formatos de LibreOffice (ODF: `.ods`, `.odt`) y los de Microsoft Office moderno (OOXML:
`.xlsx`, `.docx`). Más adelante pueden venir otros programas (presentaciones, base de datos) con la misma base.

Restricciones:

- **Escrito en Dash.** Lorraine existe también para hacer crecer Dash, como Tachyon. Lo que le falte a Dash se
  añade a Dash (tareas `D<n>`, ver [13](ingenieria/13_DASH.md)). Nada de rodeos con `@native`. C solo en
  `third_party/` (zlib, stb_truetype) y en el pegamento con esas librerías.
- **Máquina:** 68020 o mejor con FPU (MUI ya pide 68020). AmigaOS 3.1 o superior, MUI 3.8 o 5. Se compila con
  `./dash --fpu`. **Tiene que ir bien en un A1200 con 68030 real** (usuario, 2026-10-25): es la máquina de los
  objetivos de rendimiento (entorno "a1200-030" de [08](ingenieria/08_PLAN_DE_PRUEBAS.md), 68030 + 68882 sin JIT). La
  máquina rápida de Tachyon (68040 con JIT) se usa para ver la evolución, no para dar por buenos los objetivos.
  Supuesto: el 68030 lleva FPU (68881/68882). Sin FPU, los `Double` van por software y Calc será lento (R-07).
- **Licencias:** todo lo que va en el repositorio tiene que poder redistribuirse con MIT. zlib (licencia zlib) y
  stb (dominio público o MIT) valen. **El código de Ignition (GPL v3) no se copia.** Se puede leer para entender
  cómo resuelve algo, y luego se escribe de nuevo.
- **Memoria:** el Amiga tiene poca. Nada se carga entero si se puede leer a trozos. Las cifras objetivo están en
  [01](ingenieria/01_REQUISITOS.md) (RNF).

## 2. Vista general

```
                 calc/calc.dash                            write/write.dash
          ventana MUI, menús, órdenes                ventana MUI, menús, órdenes
                     │                                          │
     ┌───────────────┼───────────────┐          ┌───────────────┼────────────────┐
     ▼               ▼               ▼          ▼               ▼                ▼
  rejilla        fórmulas         filtros     pintor         maqueta          filtros
  (pintar la    lexer→parser→    ods, xlsx,  (pintar las    (líneas y        odt, docx,
   hoja)         código→eval;    csv         páginas)       páginas)          txt
     │           recálculo           │          │               │                │
     └──────► libro (modelo) ◄───────┘          └─────► documento (modelo) ◄─────┘
                     │                                          │
                     └──────────────────┬───────────────────────┘
                                        ▼
                                core/ (compartido)
   zip · xml_lector · xml_escritor · paquete (manifest, rels, content types) · utf8 · numeros (Double ↔ texto,
   formatos de número) · fechas · estilos · deshacer · fuentes · portapapeles · pdf · interfaz (piezas MUI comunes)
                                        │
                                        ▼
                       Dash (builtins, runtime) · third_party/zlib · third_party/stb
```

La regla de dependencias: `calc/` y `write/` usan `core/`. `core/` no sabe nada de `calc/` ni de `write/`. Calc y
Write no se usan entre sí.

## 3. Repositorio

Un solo repositorio, `FreeMEM/lorraine`, con la base común y los dos programas.

```
lorraine/
├── core/            módulos compartidos (.dash)
├── calc/            Lorraine Calc: calc.dash (programa), calc.dashui (ventana), módulos propios
├── write/           Lorraine Write: write.dash, write.dashui, módulos propios
├── tests/           run.py y test_*.dash (todos se ejecutan en FS-UAE); ficheros/ (corpus de documentos)
├── third_party/     zlib, stb_truetype (C, con sus licencias)
├── tools/           scripts de construcción, paquete, comparación con LibreOffice
├── iconos/          iconos de los programas y de sus documentos
├── paquete/         lo que va en el LHA de Aminet (LEEME, guía, instalador)
├── build/           lo que se compila (no va a git)
├── catalogos/       traducciones de la interfaz (.cd, .ct)
└── docs/            esta documentación
```

Cada programa es un ejecutable propio (`LorraineCalc`, `LorraineWrite`). Dash mete todo el programa en un único
fichero C, así que la base común va compilada dentro de cada uno. No hay librería compartida del Amiga: se ahorra
complejidad y la memoria repetida es poca.

## 4. La base común (`core/`)

| Módulo | Qué hace |
|---|---|
| `zip` | Lee el directorio central de un ZIP y saca una entrada a un búfer. Escribe ZIP con entradas guardadas (sin comprimir) o comprimidas. Inflate, deflate y CRC-32 con zlib (D6). |
| `xml_lector` | Lector XML por eventos ("pull"): `xml_siguiente()` devuelve inicio de elemento, atributo, texto o fin, sin construir un árbol. Espacios de nombres resueltos a un prefijo fijo de Lorraine. Lee de un búfer. |
| `xml_escritor` | Escribe XML con escapes correctos a un búfer que se vuelca al ZIP por trozos. |
| `paquete` | Lo común de los paquetes: `mimetype` y `META-INF/manifest.xml` de ODF; `[Content_Types].xml` y los `.rels` de OOXML. Detecta el formato de un fichero por su contenido, no por su extensión. Lleva la lista de pérdidas (A9) y Base64 hasta que Dash lo tenga (D34). |
| `utf8` | Recorrer, medir y convertir texto UTF-8, hasta que Dash lo tenga (D5). |
| `numeros` | `Double` ↔ texto (el más corto que vuelve al mismo número). Códigos de formato de número (`#,##0.00`, `0%`, `dd/mm/yyyy`...) leídos una vez y aplicados muchas. Separadores del idioma del usuario (D19). |
| `fechas` | Números de serie de fecha (sistema 1900 con su 29 de febrero falso, y 1904), y de vuelta a año, mes y día. |
| `estilos` | Tabla de estilos compartida: cada combinación de fuente, color, bordes y alineación se guarda una vez y las celdas o tramos de texto llevan su número. |
| `deshacer` | Pila de órdenes para deshacer y rehacer. Cada orden sabe hacerse y deshacerse. |
| `fuentes` | Medidas de las fuentes TrueType leídas de sus tablas (`cmap`, `hmtx`, `kern`), en twips, desde el H6: la maqueta usa siempre estas. Para pintar, fuentes del Amiga parecidas hasta el H8 y luego las TrueType con stb_truetype (como `fuente_web` de Tachyon), con caché de caracteres por tamaño. Ver A13. |
| `portapapeles` | Copiar y pegar con `clipboard.device` (IFF FTXT para texto), más un formato propio para pasar celdas o texto con formato entre programas de Lorraine (D18). |
| `pdf` | Exportar a PDF (fase posterior): páginas, texto con las 14 fuentes estándar de PDF, líneas, rellenos, imágenes. |
| `interfaz` | Piezas MUI comunes: diálogos de abrir y guardar con los filtros, avisos, preferencias, Acerca de. |

## 5. Lorraine Calc

### 5.1 Modelo (`calc/libro.dash`)

```
Libro ── hojas: [Hoja] ── estilos (core) ── textos: tabla de textos compartidos ── nombres definidos
  │
Hoja ── nombre ── filas: [Fila] (nil donde no hay nada) ── anchos de columna ── altos de fila ── inmovilizado
  │
Fila ── celdas: [Celda] (nil donde no hay nada)
  │
Celda ── tipo (vacía, número, texto, lógico, error, fórmula) ── valor (Double, o número de texto compartido)
      ── estilo (número) ── fórmula (nil o Formula)
```

- **Disperso por filas.** Una hoja es una lista de filas y cada fila una lista de celdas; lo vacío es `nil`. Leer
  una celda es dos índices. Una fila sin nada no gasta más que su hueco en la lista (4 bytes).
- **Textos compartidos.** Como `sharedStrings` de OOXML: cada texto distinto se guarda una vez. Una columna con
  "Málaga" mil veces gasta un texto.
- **Límites:** 1.048.576 filas y 16.384 columnas, los de Excel, para no perder datos al abrir. Lo que cabe de
  verdad lo pone la memoria.

### 5.2 Fórmulas (`calc/formula_*.dash`)

```
texto "=SUMA(A1:B3)*2"  →  lexer  →  parser  →  código (pila, en notación polaca inversa)  →  evaluador  →  valor
```

- **Una forma interna propia.** La fórmula se guarda compilada (código para una pila) y con referencias relativas a
  su celda, como R1C1. Así una fórmula copiada en mil filas es la misma fórmula: se guarda una vez.
- **Tres formas de escribirla:**
  - Al usuario, en su idioma: `=SUMA(A1:B3;2)` en español, `=SUM(A1:B3,2)` en inglés (catálogo de nombres).
  - En ODF: OpenFormula, `of:=SUM([.A1:.B3];2)`.
  - En OOXML: sin `=`, nombres en inglés y comas: `SUM(A1:B3,2)`.
- **Recálculo** (`calc/recalculo.dash`): cada fórmula apunta las celdas y rangos que lee. Al cambiar una celda se
  marcan sucias las que dependen de ella y se recalculan en orden. **El orden se saca con un bucle y una lista de
  pendientes, nunca con recursión:** una columna de 10.000 fórmulas encadenadas agotaría la pila de 16-32 KB. Las
  referencias circulares se detectan y dan error, `Err:522` como en LibreOffice (Excel avisa y deja un 0; cómo se
  guarda en cada formato: [12](ingenieria/12_FORMATOS.md) § 3.7). Las funciones volátiles (`AHORA`, `ALEATORIO`) se
  recalculan siempre.
- **Funciones** (`calc/funciones.dash`, la tabla de nombres, y `calc/funciones_*.dash`, por grupos: matemáticas,
  estadística, texto, fecha, lógica, búsqueda, información). La lista de la primera versión está en
  [01](ingenieria/01_REQUISITOS.md).
- **Formato de celda** (`calc/formato_celda.dash`): aplica el formato de número y el estilo a un valor para pintarlo.
- **Órdenes** (`calc/ordenes.dash`): cada cambio del libro como orden que se deshace (usa `core/deshacer`).

### 5.3 Pantalla (`calc/rejilla.dash`)

Una zona de dibujo MUI con doble búfer. Se pinta solo lo visible: cabeceras de filas y columnas, celdas con su
formato, la celda activa y la selección. Al cambiar una celda se repinta solo su rectángulo
(`mui_canvas_update_area`). Encima, una barra con la referencia de la celda y el campo de edición de la fórmula.

### 5.4 Filtros

`calc/ods.dash`, `calc/xlsx.dash`, `calc/csv.dash`. Cada filtro lee el fichero a eventos XML y va llenando el libro.
Nunca hay un árbol XML en memoria.

## 6. Lorraine Write

### 6.1 Modelo (`write/documento.dash`)

```
Documento ── secciones: [Seccion] (tamaño de página, márgenes, cabecera, pie)
         ── bloques: [Bloque] (párrafo o tabla)
         ── estilos (core): estilos de párrafo y de carácter con herencia
         ── imágenes, listas (numeración)

Parrafo ── texto (UTF-8) ── tramos: [Tramo] (desde, hasta, estilo de carácter) ── estilo de párrafo
       ── caché de maqueta: líneas con su ancho y alto (se tira al cambiar el párrafo)
Tabla   ── filas ── celdas ── bloques (párrafos)
```

- **Cada párrafo tiene su propio texto.** Editar cuesta lo que mide el párrafo, no el documento. Es lo más simple que
  funciona: un documento de 100 páginas tiene unos 1.500 párrafos de unos cientos de bytes.
- **Tramos con formato** en lugar de texto marcado: el texto está limpio y el formato va aparte, como los `w:r` de
  OOXML y los `text:span` de ODF.

### 6.2 Maqueta y páginas (`write/maqueta.dash`, `write/paginas.dash`)

- **Unidad interna: el twip** (1/1440 de pulgada), entero. Es la unidad de OOXML; las medidas de ODF (cm, mm, in,
  pt) se pasan a twips al leer. Todo cálculo de maqueta es con enteros: rápido en un 68k y sin redondeos que se
  acumulen.
- **Cortar líneas:** por palabras, con el ancho medido de cada tramo en su fuente. Resultado guardado en la caché del
  párrafo.
- **Paginar:** se reparten los párrafos en páginas desde el primero que cambió. Lo de antes no se toca. Control de
  viudas y huérfanas y "conservar con el siguiente" en una fase posterior.
- **Las páginas no saldrán igual que en Word ni en LibreOffice.** Las fuentes y sus medidas son otras. El objetivo es
  que el contenido y el formato se conserven, no que cada línea corte en la misma palabra.

### 6.3 Pantalla y edición

`write/pintor.dash` pinta las páginas visibles con su zoom. `write/cursor.dash` lleva la posición (párrafo y byte),
la selección y las órdenes de edición. Cada tecla cambia un párrafo, rehace su maqueta y repagina desde ahí.
`write/ordenes.dash` lleva los cambios como órdenes que se deshacen; `write/listas.dash`, la numeración de las listas.

### 6.4 Filtros

`write/odt.dash`, `write/docx.dash`, `write/txt.dash`. Igual que en Calc: a eventos, sin árbol.

## 7. Abrir y guardar

1. `paquete` detecta el formato mirando el contenido: un ZIP con `mimetype` de ODF, un ZIP con `[Content_Types].xml`,
   un XML plano de ODF (`.fods`, `.fodt`) o texto.
2. Se leen primero los estilos y después el contenido, entrada a entrada del ZIP. Cada entrada se descomprime a un
   búfer, se lee a eventos y se suelta.
3. Lo que el filtro no entiende se apunta en una lista de **pérdidas** ("gráficos", "macros", "control de cambios").
   Al guardar en el formato original con pérdidas, se avisa una vez: "Este documento tenía cosas que Lorraine no
   conserva: ...".
4. Guardar escribe a un fichero temporal en el mismo volumen y, si todo fue bien, lo cambia por el original. Un
   fallo a mitad no destruye el documento.

## 8. Decisiones

Cada decisión con su porqué. Si alguna cambia, se tacha y se añade la nueva con fecha.

| ID | Decisión | Porqué | Alternativa descartada |
|---|---|---|---|
| A1 | Un repositorio con base común y dos programas | Comparten zip, XML, números, estilos, interfaz. Un cambio en la base se prueba con los dos. | Un repo por programa: cambios repetidos y versiones que no casan. |
| A2 | Modelo interno propio. ODF y OOXML son filtros de entrada y salida | Los dos formatos son muy distintos. Un modelo propio permite editar rápido y pasar de uno a otro. | Editar el árbol XML del fichero: mucha memoria y cada formato con su propio editor. |
| A3 | Texto interno en UTF-8. En pantalla, Latin-1 al principio | Los dos formatos son UTF-8; convertir a Latin-1 al leer perdería caracteres al guardar. El Amiga pinta Latin-1, así que se convierte solo al pintar. Con TrueType (fase posterior) se pintan más caracteres. | Todo en Latin-1, como Tachyon: un `€` o un `ł` se perderían al guardar. |
| A4 | Números `Double` de 64 bits (IEEE 754) | Es lo que guardan Excel y LibreOffice: 15 cifras. Con 32 bits (7 cifras) una suma de importes ya falla. | `Float` de 32 bits: no vale. `Fixed`: poco rango. |
| A5 | Lector XML escrito en Dash | Es el camino por el que pasa todo fichero: hace crecer Dash donde más se nota (textos, búferes, velocidad). | expat en C. Se queda de reserva: si el lector en Dash va más de 3 veces más lento que expat en el H1, se decide de nuevo. |
| A6 | zlib en `third_party/`, expuesto como builtins de Dash (D6) | Comprimir es C por naturaleza y sirve a todo programa Dash (Tachyon descomprime con stb). | z.library del sistema: no todos la tienen. |
| A7 | Fórmulas compiladas, con referencias relativas, guardadas una vez | Una columna de mil fórmulas iguales gasta como una. Evaluar código es más rápido que volver a leer el texto. | Guardar el texto y leerlo cada vez. |
| A8 | Al abrir, usar el valor que trae el fichero para cada fórmula; recalcular solo lo que se sabe calcular | Un libro con funciones que Lorraine aún no tiene se ve bien igual. Abrir es más rápido. | Recalcular todo al abrir: errores donde falten funciones. |
| A9 | Lo que no se entiende no se conserva; se avisa al guardar | Conservar trozos de XML que no se entienden y que apuntan a cosas que sí se cambiaron rompe ficheros. | Guardar el XML desconocido tal cual. Se puede revisar en una fase posterior para partes enteras del paquete que nada referencia (miniaturas, propiedades a medida). |
| A10 | Unidad de maqueta: twip entero | Es la de OOXML, cabe en un `Int` (un folio A4 mide 16.838 twips de alto) y no hay coma flotante en la maqueta. | Puntos con decimales: más lento en un 68k. |
| A11 | Interfaz en inglés de base, con catálogos de varios idiomas (`tr`, `@catalog` de Dash); el español, el primero (usuario, 2026-10-25) | La comunidad Amiga es internacional. Los catálogos ya funcionan en Dash. | Solo español, como Tachyon. |
| A12 | Un ejecutable por programa | Más simple de construir y de probar. | Un único ejecutable con los dos, o una librería compartida. |
| A13 | Fuentes de Lorraine: Liberation Sans, Serif y Mono, Carlito y Caladea (licencia SIL OFL 1.1, van en el paquete). Miden lo mismo, carácter a carácter, que Arial, Times New Roman, Courier New, Calibri y Cambria. La maqueta usa siempre sus medidas, en pantalla y en PDF; el PDF las lleva incrustadas (2026-10-25) | Un documento hecho con Arial o Calibri corta las líneas donde en Word, y el PDF sale igual que la pantalla. Es lo que hace LibreOffice. | Las 14 fuentes estándar de PDF: no se incrustan, pero sus medidas no son las de pantalla y las líneas cortarían distinto. Fuentes de mapa de bits del Amiga: medidas que no son las de nadie. |

## 9. Memoria

- Los ficheros no se cargan enteros: se descomprime una entrada del ZIP a la vez y se lee a eventos.
- Calc: cada celda con valor es un struct pequeño. La meta es menos de 40 bytes por celda con número. El primer
  diseño sale a unos 44, suponiendo 16 bytes de cabecera de struct ([05](ingenieria/05_MODELO_DE_DATOS.md) § 3.11,
  que propone cómo bajar). Se mide en el H2; depende de D17.
- Calc: un dato en la fila 1.000.000 haría una lista de un millón de huecos (4 MB). Hay que evitarlo antes del H2
  (riesgo R-16).
- Write: el texto de cada párrafo más sus tramos. La caché de maqueta se puede tirar en las páginas lejanas si falta
  memoria.
- Se prueba con `--memcheck` de Dash: cero objetos vivos al cerrar un documento.

## 10. Lo que no hace la primera versión

Macros (VBA, Basic), tablas dinámicas, gráficos, formato condicional, validación de datos, control de cambios,
comentarios, notas al pie, ecuaciones, objetos incrustados, documentos cifrados con contraseña (se avisa y no se
abre), los formatos binarios antiguos (`.xls`, `.doc`), RTF. Algunos entran en fases posteriores, ver
[11](ingenieria/11_PLAN_DE_CONSTRUCCION.md).
