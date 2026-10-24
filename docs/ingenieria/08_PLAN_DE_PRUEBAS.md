# 08. Plan de pruebas

Cómo se comprobará que Lorraine cumple los requisitos de [01](01_REQUISITOS.md): niveles, entornos, el corpus de
documentos, la comparación con LibreOffice, las pruebas de aceptación (PA) y de rendimiento (PR), y los criterios para
publicar una versión. Es el **plan de partida**: las herramientas que aquí se nombran (`tests/run.py`,
`tools/corpus.py`, `tools/volcar_lo.py`...) no existen todavía; se escriben en H0 y en el hito que las pide.

## 1. Estrategia

| Nivel | Qué | Cómo | Dónde |
|---|---|---|---|
| Unidad / módulo | Cada módulo de `core/`, `calc/` y `write/` por separado, sin ventana: entrada conocida, salida esperada | `tests/test_*.dash` con `# expect-out:` | FS-UAE, A1200 + 68882, Workbench 3.1 |
| Filtros | Abrir cada documento del corpus y volcar lo leído (valores, textos, formato) en texto | `tests/test_volcar_*.dash` y `tools/comparar.py` contra el volcado de LibreOffice | FS-UAE + PC |
| Ida y vuelta | Lorraine abre y guarda; LibreOffice lee lo guardado; se compara con el original | `tools/ida_vuelta.py` | FS-UAE + PC |
| Validación | Lo que guarda Lorraine cumple el estándar | Validadores (§ 4.4) | PC |
| Memoria | Nada vivo al cerrar; sin dobles liberaciones | `# memcheck` en cada test, o `run.py --memcheck` | FS-UAE |
| Robustez | Ficheros malos no cuelgan ni pierden memoria | Corpus de ficheros malos (§ 5) con `--memcheck` | FS-UAE |
| Interfaz | Menús, teclado, ratón, ventanas | Programa entero con eventos de `input.device` y capturas (§ 6) | FS-UAE con MUI |
| Rendimiento | Tiempos y memoria de RNF | `tools/medir.py` (§ 8) | FS-UAE "medida" |
| Aceptación | Los casos de uso de [02](02_CASOS_DE_USO.md), de principio a fin | Lista manual (§ 7) | FS-UAE y, si se puede, un Amiga real |

**Reglas:**

- Sin `DASH_KICKSTART`, FS-UAE arranca con AROS y los resultados no valen.
- Nada que funcionaba puede romperse: la batería entera antes y después de cada cambio, como en Tachyon.
- Los tests no usan ficheros de fuera del repositorio salvo el corpus externo (§ 3.3), que es opcional y se salta si
  no está.
- Un fallo intermitente se da por arreglado con 20 ejecuciones limpias seguidas.

## 2. Entornos

| Nombre | Máquina emulada | Sistema | Para qué |
|---|---|---|---|
| a1200 | 68020 + 68882 | Workbench 3.1 (`sys31`) | Tests de módulos (sin MUI) |
| a1200-mui | Igual | 3.1 con MUI 5 (`sys31mui`) | Tests con ventana |
| a1200-32-mui | Igual | 3.2 con MUI 5 (`sys32mui`) | Compatibilidad con 3.2 (RNF-01) |
| a1200-030 | 68030 + 68882 sin JIT, a la velocidad de una Blizzard 1230 de 50 MHz; 16 MB de Fast (propuesta) | 3.1 con MUI 5 (`sys31mui`) | **Máquina mínima: los objetivos de rendimiento (PR) se cumplen aquí** (usuario, 2026-10-25). Cómo se ajusta FS-UAE a esa velocidad: **comprobar** en H0 |
| medida | 68040 + JIT, RTG | 3.2 con MUI 5 (el `sys32rtg` de Tachyon) | Capturas y evolución de las medidas; no da por buenos los objetivos |
| mui38 | 68040 + JIT, RTG | 3.2 con MUI 3.8 (`sys32rtg38`) | Compatibilidad con MUI 3.8 (RNF-01) |
| real | Un Amiga real o Amiberry del usuario | El suyo | Aceptación a mano, cuando haya versión |

Variables y cómo se preparan los sistemas: [09](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md).

## 3. El corpus de documentos

Vive en `tests/ficheros/`. Tres partes.

### 3.1 Corpus propio, generado

`tools/corpus.py` describe cada documento en Python (celdas, fórmulas, formatos; párrafos, estilos, tablas) y lo
escribe primero como `.fods` o `.fodt` (XML plano, fácil de generar). Después LibreOffice lo convierte al resto:

```bash
soffice --headless --convert-to ods  --outdir tests/ficheros/calc  tests/ficheros/calc/fuente/*.fods
soffice --headless --convert-to xlsx --outdir tests/ficheros/calc  tests/ficheros/calc/fuente/*.fods
soffice --headless --convert-to csv  --outdir tests/ficheros/calc  tests/ficheros/calc/fuente/*.fods
soffice --headless --convert-to odt  --outdir tests/ficheros/write tests/ficheros/write/fuente/*.fodt
soffice --headless --convert-to docx --outdir tests/ficheros/write tests/ficheros/write/fuente/*.fodt
```

Así cada caso existe en todos los formatos y se regenera con una orden. La versión de LibreOffice usada se apunta en
`tests/ficheros/VERSION` (los ficheros cambian un poco entre versiones).

Casos mínimos de partida (se amplían en cada hito):

| Grupo | Casos |
|---|---|
| Calc, valores | Números enteros, decimales, grandes, pequeños, negativos, `0,1+0,2`; textos con acentos, `€`, emojis y otros alfabetos (A3); fechas en 1900 y 1904; lógicos; errores (`#DIV/0!`, `#N/A`...); celdas vacías en medio; última fila y columna de Excel |
| Calc, fórmulas | Una hoja por grupo de funciones de [01](01_REQUISITOS.md) § 3.3; referencias relativas, absolutas, mixtas, a otras hojas, a nombres; una columna de 1.000 fórmulas iguales (A7); circulares; volátiles |
| Calc, formato | Cada formato de número; fuentes, colores, bordes, alineación; anchos y altos; combinadas; ocultas; inmovilizado |
| Calc, tamaño | El libro de RNF-C01 (20.000 celdas, 2.000 fórmulas); uno de 100.000 celdas para ver los límites |
| Write, texto | Párrafos con acentos, `€`, otros alfabetos; tramos con cada formato de carácter; cada alineación; sangrías e interlineados; estilos con herencia |
| Write, estructura | Saltos de página y línea; listas de varios niveles; tablas (con celdas combinadas); imágenes PNG, JPEG y GIF; cabecera y pie con número de página; secciones con otra orientación |
| Write, tamaño | El documento de RNF-W01 (50 páginas); uno de 300 páginas |
| Pérdidas (A9) | Un libro con gráfico y otro con macros; un documento con control de cambios y otro con notas al pie: deben dar el aviso M-07 |

### 3.2 Volcado de referencia

`tools/volcar_lo.py` saca de cada documento, con LibreOffice, un volcado en texto con el que se comparan las salidas
de Lorraine. Propuesta: una macro en Python que corre en `soffice --headless` por UNO (`python3` con el módulo `uno`
del LibreOffice instalado).

- **Calc:** por cada celda no vacía, una línea: `hoja!A1 <tipo> <valor exacto> <texto mostrado> <fórmula>`. El valor
  exacto de un número con 17 cifras significativas (vuelve al mismo `Double`).
- **Write:** por cada párrafo, su estilo y su texto; por cada tramo, su formato de carácter; tablas como filas de
  celdas; imágenes con su tamaño.

Lorraine escribe el mismo volcado desde los tests (`test_volcar_*.dash`) y `tools/comparar.py` compara las dos
salidas línea a línea con la tolerancia del § 4.3.

### 3.3 Corpus externo, de ficheros reales

Ficheros hechos con Microsoft Office de verdad, para lo que LibreOffice no genera igual (sobre todo `.xlsx` y `.docx`
de Excel y Word). **No van al repositorio:** `tools/corpus_externo.sh` los bajaría a `~/.cache/lorraine-corpus/` y los
tests que los usan se saltan si no están, porque su licencia no siempre es compatible con MIT (RNF-06).

Candidatos, **sin revisar todavía su licencia ni su contenido**:

- Los ficheros de prueba de Apache POI (`test-data/spreadsheet` y `test-data/document`), con licencia Apache 2.0.
- Los documentos de prueba de LibreOffice (`sc/qa/unit/data` y `sw/qa/extras/*/data` del repositorio `core`),
  con licencia MPL 2.0.

Tarea de H0: revisar los dos, elegir unos 50 ficheros de cada programa y apuntar de dónde sale cada uno.

## 4. Comparaciones

### 4.1 Filtros (lectura)

Cada documento del corpus, abierto por Lorraine, da el mismo volcado que LibreOffice. Las diferencias admitidas se
apuntan en `tests/ficheros/diferencias.txt` con su porqué (por ejemplo: un formato que Lorraine aún no tiene, o la
paginación de Write, que no se compara).

### 4.2 Ida y vuelta (escritura)

```
original.ods ──Lorraine abre y guarda──► lorraine.ods ──volcar_lo.py──► volcado B
original.ods ─────────────volcar_lo.py────────────────────────────────► volcado A
                                                         comparar.py A B ⇒ iguales
```

Para cada formato de salida (`.ods`, `.fods`, `.xlsx`, `.csv`, `.odt`, `.fodt`, `.docx`, `.txt`) y cada documento del
corpus. También cruzado: abrir `.xlsx` y guardar `.ods`, y al revés. Lorraine corre en FS-UAE. El disco del emulador
(`DH0:`) es una carpeta del PC que monta `tools/emu_run.py` de Dash: el corpus se copia ahí antes de arrancar, y lo
que Lorraine guarda se recupera con `--keep` para que LibreOffice lo vuelque en el PC.

### 4.3 Tolerancia de los números

Los `Double` se comparan así:

- **Valores leídos de un fichero** (sin calcular): iguales bit a bit. Leer y escribir un número no puede cambiarlo.
- **Valores calculados por Lorraine:** `|a − b| ≤ 1e-12 × max(1, |a|, |b|)`.
- **Funciones con algoritmo iterativo o de otro orden de suma** (IRR, RATE, STDEV, VAR, PERCENTILE y las que se
  apunten): `1e-9` relativo. La lista está en `tools/comparar.py`.
- **Fechas y horas:** iguales al segundo.
- **Textos mostrados** (formato de número aplicado): iguales carácter a carácter.

### 4.4 Validadores y lectores independientes

Excel y Word no se usan (decisión del usuario, 2026-10-25). Un fichero que guarda Lorraine se da por bueno si lo
aceptan un validador y **tres lectores escritos por gente distinta**: LibreOffice, OnlyOffice y las librerías de
Python. Cada uno perdona errores distintos; juntos se parecen más a lo que exigiría Excel.

| Formato | Herramienta | Qué comprueba | Estado en este PC |
|---|---|---|---|
| ODF (`.ods`, `.odt`, `.fods`, `.fodt`) | ODF Validator del ODF Toolkit (`tdf/odftoolkit`, Apache 2; la 0.13.0 es de enero de 2026) | Esquema RELAX NG y reglas del paquete | Hay `java`; el `.jar` se baja en H0 a `~/.cache/lorraine-tools/` |
| OOXML (`.xlsx`, `.docx`) | OOXML-Validator (`mikeebowen/OOXML-Validator`, MIT), que usa el validador del Open XML SDK de Microsoft | Esquemas de ECMA-376 / ISO/IEC 29500, como Office | Necesita .NET. Se instala **sin tocar el sistema** en `~/.cache/lorraine-tools/dotnet` con `dotnet-install.sh` (tarea de H0; **comprobar** que funciona así) |
| Todos | LibreOffice sin pantalla: `soffice --headless --convert-to` y el volcado de `tools/volcar_lo.py` | Que abre sin reparar y con el mismo contenido | `soffice` instalado |
| Todos | OnlyOffice: su conversor sin pantalla `x2t` (`/opt/onlyoffice/desktopeditors/converter/x2t`), de `.xlsx`/`.docx` a `.ods`/`.odt`/PDF | Otro motor, más cercano en su lectura de OOXML al de Microsoft | Instalado. Cómo se le pasan las órdenes a `x2t` (un XML de parámetros): **comprobar** en H0 |
| `.xlsx`, `.docx` | openpyxl y python-docx, en un `venv` de `~/.cache/lorraine-tools/` | Que leen el fichero y dan los mismos valores y textos | Se instalan en H0 (hoy no están) |
| ZIP | `unzip -t` | El paquete | Está |

### 4.5 Cobertura de las normas

**No existe una batería oficial que diga "soporte completo"** de ODF ni de OOXML. El comité OASIS que lo intentó para
ODF (OIC) no publica software de conformidad, y para OOXML no hay nada parecido. Además, un fichero válido no prueba
que el programa soporte toda la norma. Por eso se miden cuatro cifras en cada versión (RNF-08), que salen en las
notas y en el panel de progreso:

| Cifra | De dónde sale | Cómo se mide | Desde |
|---|---|---|---|
| **Funciones de Calc** | Los tests de funciones de LibreOffice (`sc/qa/unit/data/functions/<grupo>/fods/<función>.fods` del repositorio `core`): un fichero por función (147 de estadística, 79 de matemáticas, y de fecha, texto, lógica, búsqueda, financieras, información, base de datos, matrices). Cada uno se comprueba solo: su hoja tiene una celda "Result" | `tools/funciones_lo.py` los baja a `~/.cache/lorraine-pruebas/` (licencia de LibreOffice, no MIT: no van al repo). Lorraine abre cada uno en el emulador, recalcula todo y escribe el valor de la celda de resultado. Cifra: funciones que pasan / funciones que hay | H3 |
| **Atributos de ODF conservados** | ODFAutoTests (Jos van den Oever, de los plugfests de ODF): cientos de pruebas pequeñas sacadas de la norma. Cada una crea un documento con un atributo y mira si el programa lo conserva al abrir y guardar | Hace falta un adaptador que pase cada documento por Lorraine en el emulador. **Comprobar** en H3 si el proyecto sigue mantenido y cómo se ejecuta | H3 (Calc), H7 (Write) |
| **Errores de validación** | § 4.4 | Todo lo que guarda la ida y vuelta del corpus, por cada validador. Objetivo: cero | H3 |
| **Ida y vuelta** | El corpus (§ 3) | Documentos que vuelven iguales / documentos del corpus | H3 |

Para OOXML, además de los validadores, la referencia de cómo se aparta Office de la norma son las notas de Microsoft
[MS-OI29500] (Office y la ISO/IEC 29500) y [MS-OE376] (Office y la ECMA-376). Se consultan al escribir los filtros
([12](12_FORMATOS.md) § 10).

## 5. Corpus de ficheros malos

En `tests/ficheros/malos/`, generados por `tools/corpus_malo.py` a partir del corpus bueno:

| Caso | Qué se espera |
|---|---|
| Truncado (a la mitad, a 10 bytes, vacío) | M-02, sin colgarse |
| ZIP con el directorio central roto, con CRC mal, con una entrada que dice medir 4 GB | M-02 |
| XML mal formado (etiqueta sin cerrar, entidad desconocida, UTF-8 inválido) | M-02 |
| Entradas que faltan (`content.xml`, `workbook.xml`, una hoja) | M-02 |
| Referencias rotas (estilo que no existe, texto compartido fuera de rango, relación sin destino) | Abre lo que puede, con valores por omisión |
| Cifrado (ODF con `manifest:encryption-data`, OOXML cifrado) | M-03 |
| `.xls` y `.doc` binarios | M-05 |
| Bomba de ZIP (una entrada que se descomprime a cientos de MB) | M-06 o M-02, sin agotar la memoria del sistema |
| Fórmulas absurdas (anidadas 1.000 veces, de 10 KB) | Error en la celda, sin desbordar la pila |

Todos con `--memcheck`: cero objetos vivos al acabar (RNF-02, RNF-03).

## 6. Pruebas de la interfaz

Como en Dash y en Tachyon: el programa entero en FS-UAE con MUI, y un proceso auxiliar que manda eventos reales por
`input.device` (teclas, movimientos y clics; para los menús, botón derecho sobre el título y movimientos relativos de un
paso). El resultado se comprueba por:

- La salida del programa en modo de prueba (propuesta: con un argumento `TEST`, cada orden escribe una línea con su
  efecto, por ejemplo `celda B4 = 391.5`).
- Capturas (`tools/emu_run.py --screenshot` de Dash) que se miran a mano en cada hito, no se comparan píxel a píxel.

Los procesos auxiliares acaban antes que el programa; si no, cuelgan los siguientes del mismo arranque (aviso del
`AGENTS.md` de Dash).

## 7. Pruebas de aceptación (PA)

A mano, al cerrar cada hito, siguiendo los casos de uso de [02](02_CASOS_DE_USO.md). Una PA pasa si se hace de
principio a fin sin errores ni pérdidas.

| ID | Prueba | Requisitos | Hito |
|---|---|---|---|
| PA-N01 | Abrir por diálogo, por Shell y por icono un documento de cada formato | RF-N01, RF-N02 | H2 / H6 |
| PA-N02 | Abrir cada fichero malo: aviso claro, programa usable | RF-N03, RNF-03 | H2 / H6 |
| PA-N03 | Editar, cerrar sin guardar (pregunta), guardar, reabrir: igual | RF-N04, RF-N07 | H3 / H7 |
| PA-N04 | Cortar la escritura a mitad (disco lleno simulado): el original queda intacto | RF-N05 | H3 |
| PA-N05 | Abrir un documento con gráfico o macros y guardar: aviso con la lista | RF-N06 | H3 / H7 |
| PA-N06 | 100 cambios, deshacer los 100, rehacer los 100: igual cada vez | RF-N08 | H3 / H7 |
| PA-N07 | Copiar texto de otro programa del Amiga y pegarlo; copiar celdas a Write | RF-N09 | H5 / H7 |
| PA-N08 | Dos documentos abiertos a la vez, cambios en los dos, salir: pregunta por cada uno | RF-N10 | H5 / H7 |
| PA-N09 | Con el sistema en español, menús y avisos en español | RF-N14 | H5 |
| PA-C01 | Presupuesto doméstico: escribir conceptos e importes, sumas, porcentajes, formato de moneda, guardar `.ods` y `.xlsx`, abrir los dos en LibreOffice | RF-C02, RF-C03, RF-C06, RF-C10, RF-C12 | H4 |
| PA-C02 | Abrir un `.xlsx` de Excel del corpus externo, cambiar un dato, ver el recálculo, guardar | RF-C01, RF-C09, RF-C11 | H3 |
| PA-C03 | Seleccionar con teclado y ratón todos los casos de § 2.4 y 2.5 de [06](06_INTERFAZ_DE_USUARIO.md) | RF-C07 | H3 |
| PA-C04 | Insertar y borrar filas y columnas con fórmulas que apuntan a través: siguen bien | RF-C16 | H5 |
| PA-C05 | Rellenar series, ordenar, buscar y reemplazar, inmovilizar | RF-C17 a RF-C20 | H5 |
| PA-C06 | Importar un CSV con punto y coma y Latin-1; exportarlo con coma y UTF-8 | RF-C01, RF-C04 | H4 |
| PA-W01 | Carta: escribir, dar formato, alinear, guardar `.odt` y `.docx`, abrir en LibreOffice | RF-W02, RF-W05 a RF-W07 | H7 |
| PA-W02 | Abrir un `.docx` de Word del corpus externo, corregir, guardar | RF-W01, RF-W02 | H7 |
| PA-W03 | Informe con estilos, listas, una tabla, una imagen, cabecera y pie | RF-W08, RF-W11 a RF-W14 | H8 |
| PA-W04 | Buscar y reemplazar, contar palabras | RF-W09, RF-W16 | H7 |

## 8. Pruebas de rendimiento (PR)

Con `tools/medir.py` (propuesta, como `medir_visor.py` de Tachyon): arranca el programa en "a1200-030" (los objetivos)
y en "medida" (la evolución) con
un documento y una lista de órdenes, y apunta tiempos (`time_ms`) y memoria (libre al empezar y tras abrir). Se
guardan en `tests/bench/resultados.json` con el commit, para ver la evolución. Cada cifra es la mediana de 5
ejecuciones.

| ID | Medida | Objetivo | Requisito | Desde |
|---|---|---|---|---|
| PR-C01 | Abrir el libro de 20.000 celdas y 2.000 fórmulas (`.ods` y `.xlsx`) | < 5 s | RNF-C01 | H2 |
| PR-C02 | Cambiar una celda de la que dependen 100 fórmulas en cadena normal | < 0,2 s | RNF-C02 | H3 |
| PR-C03 | Memoria con ese libro abierto | < 8 MB | RNF-C03 | H2 |
| PR-C04 | Repintar la rejilla al desplazar una pantalla | < 50 ms | RNF-C04 | H2 |
| PR-C05 | Guardar ese libro (`.ods` y `.xlsx`) | Sin objetivo: se mide | — | H3 |
| PR-W01 | Abrir el documento de 50 páginas (`.odt` y `.docx`) | < 5 s | RNF-W01 | H6 |
| PR-W02 | Escribir una tecla al principio de ese documento, hasta verla | < 50 ms | RNF-W02 | H7 |
| PR-W03 | Memoria con ese documento abierto | < 8 MB | RNF-W03 | H6 |
| PR-B01 | Lector XML con el `content.xml` más grande del corpus, frente a expat compilado para 68k | ≤ 3 veces más lento (decisión A5) | — | H1 |
| PR-B02 | Descomprimir 1 MB con zlib | Se mide | — | H1 |
| PR-B03 | Bytes por celda con número (decisión de memoria § 9 de la arquitectura) | < 40 | RNF-C03 | H2 |

## 9. Criterios para publicar una versión

Una versión (ver [11](11_PLAN_DE_CONSTRUCCION.md) § 3) se publica si:

1. La batería entera pasa en a1200, a1200-mui y a1200-32-mui, también con `--memcheck`.
2. El corpus de ficheros malos no cuelga ni pierde memoria.
3. La ida y vuelta de todo el corpus de los formatos de esa versión da los mismos volcados (salvo
   `diferencias.txt`).
4. Lo que guarda pasa los validadores y lo abren los tres lectores de § 4.4. Las cuatro cifras de cobertura (§ 4.5) no
   bajan respecto a la versión anterior y salen en las notas.
5. Las PA de los hitos que entran pasan, y las PR están dentro del objetivo en "a1200-030" o la diferencia se explica
   en las notas.
6. El paquete se instala en un sistema limpio con 3.1 y con 3.2 y abre el corpus ([09](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md)).
7. Revisión de licencias de `third_party/` (RNF-06).
