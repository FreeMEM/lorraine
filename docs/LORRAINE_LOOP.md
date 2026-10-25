# Lorraine: plan de trabajo (para `/loop`)

Arranque (desde cualquier directorio):

```
/loop Sigue las instrucciones de ~/Projects/lorraine/docs/LORRAINE_LOOP.md: haz UNA tarea y actualiza la bitácora. No hagas pausas entre vuelta y vuelta
```

## Objetivo

Lorraine Calc y Lorraine Write para AmigaOS 3.x, con interfaz MUI, escritos en Dash, que abren y guardan ODF y OOXML.
El diseño está en `docs/ARQUITECTURA.md` y `docs/ingenieria/` (empieza por `00_INDICE.md`). **Este plan sigue los hitos
de `docs/ingenieria/11_PLAN_DE_CONSTRUCCION.md`**; si algo de aquí choca con el diseño, gana el diseño y se apunta en la
bitácora.

**Lorraine existe para hacer crecer Dash** (usuario, 2026-10-24): lo que le falte a Dash se añade a Dash (tareas `D<n>`
de `docs/ingenieria/13_DASH.md`). Nada de rodeos con `@native`: C solo en `third_party/` y su pegamento.

**Interfaz: MUI, siempre** (usuario, 2026-10-25). Nada de GadTools, ReAction ni ventanas de Intuition sueltas para la
interfaz; lo que le falte a Dash de MUI es una tarea D.

Máquina (usuario, 2026-10-25): **tiene que ir bien en un A1200 con 68030 y FPU real**. Los objetivos de rendimiento se
miden en el entorno "a1200-030" (`08_PLAN_DE_PRUEBAS.md` § 2). Se compila con `./dash --fpu`.

## Reglas de cada iteración

1. **Uso.** Si el uso semanal pasa del 90 %, apúntalo en la bitácora, para el loop y avisa con PushNotification.
2. **Rama.** Trabaja en `~/Projects/lorraine`, rama `dev` (sale de `main`). Sin push ni PR: eso lo pide el usuario.
3. **Dash.** Las tareas `D<n>` las hace este mismo loop, una por iteración, en el worktree
   `~/Projects/FreeMEMLang/.worktrees/lorraine` (rama `lorraine`, sale de `main` de FreeMEM/dash), con su test en la
   batería de Dash (`python3 tests/run_tests.py`, antes y después) y su commit allí: `lorraine D<n> - <resumen>`.
   Con el estilo de Dash: builtins en inglés, `docs/BUILTINS.md` regenerado (`tools/gen_builtins_doc.py`), runtime
   `_dash_*`, en diccionarios y plantillas propios para no chocar con las ramas `dashweb` y `mui`.
   - Del resto de `~/Projects/FreeMEMLang` no se toca nada: ni `main`, ni el worktree `dashweb` (Tachyon), ni otros.
   - Antes de hacer una D, mira si ya existe en `main` de Dash o en la rama `dashweb` (`git log`, `docs/BUILTINS.md`).
     Si existe en `dashweb` y no en `main`, apúntalo y pregunta al usuario antes de duplicarla.
4. **Base.** `python3 tests/run.py` (cuando exista) antes de empezar. Anota si cambia respecto a la última entrada.
5. **Tarea.** Coge la primera tarea `[ ]` de la lista, en orden. Si necesita una D que no está hecha, haz la D primero
   (es la tarea de esta iteración). Márcala `[~]` mientras trabajas. Una por iteración. Si es grande, divídela en la
   lista y haz solo la primera parte. Al llegar a un hito sin dividir, divídelo en tareas según el 11 y haz la primera.
6. **Hacer.** Código en `core/`, `calc/`, `write/`, con los nombres de `07_MODULOS_E_INTERFACES.md` (si cambian,
   actualiza el 07). Cada cosa con su test en `tests/`, ejecutado en el emulador. Antes de escribir Dash, lee
   `~/Projects/FreeMEMLang/docs/SINTAXIS.md`. Entorno (no va al repo): las variables de
   `09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md` § 3. **Sin `DASH_KICKSTART` se usa la ROM AROS y los resultados no valen.**
7. **Verificar.** Repite el paso 4. Nada que antes funcionaba puede romperse. Si algo se rompe y no lo arreglas en
   esta iteración, revierte.
8. **Capturas** (usuario, 2026-10-25: "ve mostrándome capturas de cómo va quedando"). Cuando una tarea cambie algo que
   se ve en el Amiga, saca una captura del emulador (`$DASH/tools/emu_run.py --autoclose 30 --screenshot 20 x.png
   prog.dash`), mírala con Read y envíasela al usuario con SendUserFile en ese momento, con una línea de qué se ve.
   Las capturas se guardan en `docs/img/` si sirven para la documentación; si no, en el scratchpad.
9. **Cerrar.** Marca `[x]`, añade una entrada a la bitácora (qué se hizo, medidas, decisiones, lo que queda) y haz
   commit local `<tarea> - <resumen>`. Si la tarea cambió el diseño, actualiza el documento de `docs/ingenieria/` que
   toca en el mismo commit.
10. **Fin.** Si no quedan tareas `[ ]`, escribe el resumen final, para el loop y avisa con PushNotification.

## Límites

- No instales paquetes del sistema. En `~/.cache/lorraine-tools/` sí vale: `venv`, `.jar`, .NET con
  `dotnet-install.sh`.
- Nada en git que no sea compatible con MIT: tests de LibreOffice (MPL), corpus externo, SDK de MUI, ROMs, Workbench.
  Lo bajan scripts a `~/.cache`.
- **El código de Ignition (GPL v3) no se copia** ni se tiene abierto mientras se escribe su equivalente.
- Procesos: para solo los tuyos, por PID (nada de `pkill fs-uae`). Si `ListAgents` muestra sesiones de Dash o de
  Tachyon, avísalas antes de una batería larga del emulador.
- Si una tarea exige una decisión del usuario, déjala `[?]` con la pregunta y pasa a la siguiente.

## Tareas

### H0 Entorno, tests y corpus

- [x] 0.1 Rama `dev` en Lorraine. Worktree de Dash `.worktrees/lorraine` (rama `lorraine` desde `main`). Dash compila
      un hola con `--fpu`.
- [x] 0.2 `tests/run.py` (del de Tachyon, adaptado: `$DASH` por omisión el worktree `lorraine`; entornos a1200,
      a1200-mui y a1200-030) y `tests/test_hola.dash`, que pasa en FS-UAE con la ROM 3.1. Captura de una ventana MUI
      de prueba con el nombre de Lorraine.
- [x] 0.3 Entorno "a1200-030": FS-UAE con 68030 + 68882, sin JIT, a la velocidad de una Blizzard 1230 de 50 MHz
      (averiguar las opciones; apuntar cómo se comprobó). Un bucle de referencia medido en los tres entornos.
- [x] 0.4 `tools/corpus.py`: corpus propio con `soffice --headless` en `tests/ficheros/` (Calc: valores, fórmulas,
      formatos, varias hojas, fechas, límites, 20.000 celdas; Write: texto, estructura, 50 páginas), en todos los
      formatos.
- [x] 0.4b Corpus, segunda parte: pérdidas (libro con gráfico y con macros; documento con control de cambios y
      con notas al pie), imágenes JPEG y GIF, libro de 100.000 celdas y documento de 300 páginas, inmovilizado.
- [x] 0.5 `tools/volcar_lo.py`: volcado de referencia (valores de celdas, texto y formato de párrafos).
- [~] 0.6 Herramientas de comprobación (`08` § 4.4) en `~/.cache/lorraine-tools/`: ODF Validator, .NET y
      OOXML-Validator, `venv` con openpyxl y python-docx, parámetros del `x2t` de OnlyOffice. `tools/comprobar.py`
      pasa un fichero por todas y resume.
- [ ] 0.7 `tools/funciones_lo.py`: baja los tests de funciones de LibreOffice a `~/.cache/lorraine-pruebas/` y los
      cuenta por grupo (`08` § 4.5).
- [ ] 0.8 Corpus de ficheros malos en `tests/ficheros/malos/` (`08` § 5).
- [ ] 0.9 Corpus externo: revisar licencias (Apache POI, LibreOffice), elegir unos 50 ficheros de cada programa,
      `tools/corpus_externo.sh` a `~/.cache/lorraine-corpus/`.

### H1 Base: ZIP, XML, UTF-8, paquetes

- [ ] D6 Comprimir en Dash: `inflate`, `deflate`, `crc32` con zlib.
- [ ] D5 UTF-8 en Dash.
- [ ] 1.1 `core/zip`: leer (directorio central, entradas guardadas y comprimidas). Test contra `unzip -l` y `unzip -p`.
- [ ] 1.2 `core/zip`: escribir (guardadas, con CRC). `unzip -t` sin errores.
- [ ] 1.3 `core/xml_lector`: eventos, atributos, entidades, CDATA, espacios de nombres. Tests.
- [ ] 1.4 PR-B01: el lector contra expat compilado para 68k (en el scratchpad, no va al repo), en "a1200-030". Si va
      más de 3 veces más lento, `[?]` para el usuario (decisión A5).
- [ ] 1.5 `core/xml_escritor`.
- [ ] 1.6 `core/paquete`: detectar el formato, manifiesto, `[Content_Types].xml`, relaciones; OLE2 da su aviso.
- [ ] 1.7 Prueba de todo el corpus: entradas y texto del XML principal, igual que en el PC.

### H2 Calc: visor

- [ ] D1 `Double` en Dash.
- [ ] D3 `Double` a texto y de texto, exactos.
- [ ] D9 Diccionarios con clave `Int`.
- [ ] D31 Argumentos del Workbench.
- [ ] D17 Medir la cabecera de los structs (solo medir; reducirla, en H5 si hace falta).
- [ ] 2.1 `calc/libro`: el modelo. Decidir R-16 (filas dispersas). PR-B03 (bytes por celda).
- [ ] 2.2 `core/numeros` y `core/fechas`: códigos de formato de número (leer y aplicar), series de fecha.
- [ ] 2.3 `calc/ods`: leer `.ods` y `.fods` con el valor guardado de las fórmulas (A8).
- [ ] 2.4 `calc/xlsx`: leer `.xlsx` (textos compartidos, estilos, formatos de número, fórmulas compartidas).
- [ ] 2.5 `calc/csv`: leer `.csv`.
- [ ] 2.6 Volcado de Lorraine contra el de LibreOffice para todo el corpus de Calc.
- [ ] 2.7 `core/interfaz` y `calc/calc.dashui`: ventana, abrir, avisos, Acerca de. Captura.
- [ ] 2.8 `calc/rejilla`: pintar, desplazar, pestañas de hojas. Captura. PR-C01, PR-C03 y PR-C04 en "a1200-030".
- [ ] 2.9 Los tests de funciones de LibreOffice se abren todos sin error (con sus valores guardados).

### Hitos siguientes (se dividen al llegar, regla 5)

- [ ] H3 Calc: edición y fórmulas, guarda `.ods`.
- [ ] H4 Calc: formato y `.xlsx`.
- [ ] H5 Calc: completa, versión alfa.
- [ ] H6 Write: visor.
- [ ] H7 Write: edición, guarda `.odt` y `.docx`.
- [ ] H8 Write: listas, tablas, imágenes, TrueType; versión alfa.
- [ ] H9 PDF para los dos.
- [ ] H10 Imprimir.
- [ ] H11 Paquete y versión 1.0.

## Bitácora

Plantilla:

```
### AAAA-MM-DD — Tarea N (resumen)

- Qué se hizo. Medidas. Decisiones y su porqué. Lo que queda.
- Batería: N/M.
```

### 2026-10-25 — Plan

- Documentación de ingeniería escrita (`docs/ingenieria/`, 00 a 13) y repositorio `FreeMEM/lorraine` creado.
- Decisiones del usuario: licencia MIT, nombre Lorraine, A1200 con 68030 real como máquina mínima, inglés de base
  con catálogos, fuentes Liberation/Carlito/Caladea para la maqueta y el PDF (A13), sin Excel ni Word (se comprueba
  con LibreOffice, OnlyOffice y librerías de Python), capturas al usuario según se avanza.

### 2026-10-25 — Tarea 0.1 (rama y worktree de Dash)

- Rama `dev` de Lorraine (sale de `main`, que ya está en GitHub). Worktree de Dash
  `~/Projects/FreeMEMLang/.worktrees/lorraine`, rama `lorraine`, desde `main` de Dash (`8cce93e`).
- Un hola compilado con `./dash --fpu` (`-m68020 -m68881`, 4,4 KB) da su salida en FS-UAE con la ROM 3.1 y 68882
  (`tools/emu_run.py --fpu --set fpu=68882`).
- Aviso: `docs/SINTAXIS.md` de Dash está sin commit en `~/Projects/FreeMEMLang` (no está en `main` ni en este
  worktree). Se lee de ahí, por ruta absoluta, como hace Tachyon.
- Batería: aún no hay (tarea 0.2).

### 2026-10-25 — Tarea 0.2 (runner de tests y primera ventana MUI)

- `tests/run.py`, del de Tachyon: compila con `--fpu` y el Dash de `$DASH` (por omisión el worktree `lorraine`),
  ejecuta en FS-UAE y compara la salida. Directivas: `expect-out`, `memcheck`, `autoclose` (modo de prueba de MUI,
  `DASH_TEST_AUTOCLOSE`), `dash-flags`, `cflags`, `emu-config`, `emu-needs` (`muimaster.library` arranca con
  `$DASH_EMU_SYS_MUI`; la librería está en `MUI/Libs`) y `screenshot` (una captura; el test arranca solo). Compila
  también `calc/calc.dash` y `write/write.dash` cuando existan. El entorno "a1200-030" llega con la 0.3.
- `test_hola` (texto y un `Float`) y `test_ventana` (ventana MUI con el nombre de la suite y captura en
  `docs/img/h0_ventana.png`, enviada al usuario).
- `--memcheck` no imprime resumen en un programa que no reserva memoria del pool: `test_ventana` no lo espera.
- Batería: 2/2 (22 s).

### 2026-10-25 — Tarea 0.3 (entorno a1200-030)

- `tools/medir_cpu.dash`: 5 millones de vueltas de `subq.l #1,d0 / bne.s` (unos 8 ciclos cada una en un 68030 con
  caché: 0,8 s a 50 MHz) y un trabajo de Dash con textos y listas.
- **FS-UAE 3.2.35 no cambia la velocidad de un 68030 con `uae_cpu_multiplier`** (4, 14 y 28 dan lo mismo, también
  con `uae_cpu_frequency`, ciclo exacto completo, CPU compatible y Fast de Zorro III; la configuración UAE sí los
  recibe). Siempre sale la velocidad del A1200 de serie.
- Lo que funciona: velocidad máxima sin JIT frenada con `uae_cpu_throttle = -880`. Medido: 51, 47 y 54 MHz
  estimados con el PC cargado (carga media de 10 a 15): ±7 %. Por eso cada medida de rendimiento pasará antes el
  bucle y se normalizará a 50 MHz.
- Bucle de referencia: a1200 de serie 2898 ms (14 MHz), a1200-030 unos 780 ms (50 MHz), rtg (68040 + JIT) 46 ms.
  El trabajo de Dash: 1062, unos 320 y 13 ms.
- `tests/run.py --maquina a1200-030`. `08` § 2 al día.
- Batería: 2/2 en a1200 y 2/2 en a1200-030.

### 2026-10-25 — Tarea 0.4 (corpus propio)

- `tools/corpus.py` escribe las fuentes en Flat ODF (`tests/ficheros/<calc|write>/fuente/`) y LibreOffice 26.8.1.1
  (perfil propio en `build/lo-perfil`) las convierte: Calc a `.ods`, `.xlsx`, `.csv` (UTF-8, solo la primera hoja)
  y `.fods` con los valores calculados; Write a `.odt`, `.docx`, `.txt` y `.fodt`. 9 s todo; 7,7 MB.
- Calc: `valores` (números extremos, `0,1+0,2`, acentos, `€`, otros alfabetos, emoji, fecha, hora, lógicos, cuatro
  errores, huecos), `fechas1904` (sale `date1904="true"` en el `.xlsx`), `limites` (algo en XFD1048576; el `.xlsx`
  lo conserva), `formulas` (una hoja por grupo de funciones de H3, referencias de todo tipo, un nombre, 1.000
  fórmulas iguales, una circular que da `Err:522`, `RAND`), `formato` (10 formatos de número, fuente, colores, bordes,
  alineación, ajuste, anchos, fila alta, fila y columna ocultas, combinada 2x3), `tamano_20k` (20.000 celdas, 2.000
  fórmulas).
- Write: `texto` (cada formato de carácter, alineaciones, sangrías, interlineado, estilos con herencia, salto de
  línea y tabulador), `estructura` (listas de dos niveles, tabla con combinada, PNG en línea, salto de página,
  sección apaisada, cabecera y pie con número de página: 4 páginas), `tamano_50p` (50 páginas medidas con el PDF de
  LibreOffice).
- **Aviso:** el CSV de `limites` salía de 16 GB (comas hasta XFD en un millón de filas). Borrado; ese caso ya no se
  pasa a CSV. El disco de `/home` está al 95 % (54 GB libres).
- Pendiente en la 0.4b: pérdidas, JPEG y GIF, los tamaños grandes, inmovilizado (va en `settings.xml`).
- Batería: 2/2 (sin cambios de código Dash).

### 2026-10-25 — Tarea 0.4b (corpus, segunda parte)

- Calc: `perdidas_grafico` (el gráfico lo añade LibreOffice por UNO: `Object 1` en el `.ods`, `xl/charts/chart1.xml`
  en el `.xlsx`), `perdidas_macros` (macro de Basic en la fuente; el `.ods` la lleva en `Basic/`), `inmovilizado`
  (fila 1 y columna A, escrito en `office:settings` de la fuente).
- Write: `imagenes` (PNG, JPEG y GIF en línea; JPEG y GIF salen del PNG con `magick`; el `.docx` lleva las tres),
  `perdidas_notas` (nota al pie y al final: `footnotes.xml` y `endnotes.xml`), `perdidas_cambios` (una inserción y un
  borrado sin aceptar: `w:ins` y `w:del`).
- Grandes, con `--grandes`, en `tests/ficheros/grandes/` (en `.gitignore`, 12 MB): libro de 100.000 celdas y
  documento de 302 páginas.
- Aprendido de LibreOffice sin pantalla: un documento oculto no guarda su vista, así que `freezeAtPosition` por UNO
  no llega al fichero. Con el inmovilizado escrito en la fuente, el `.xlsx` sale con `<pane ... state="frozen"/>`
  pero el `.ods` y el `.fods` convertidos lo pierden: para ODF la referencia es la fuente.
- LibreOffice 26.8 escribe `office:version="1.4"`: los filtros de ODF tienen que leer 1.4 (ver `12` § 2.2).
- Regenerar el corpus cambia todos los ZIP (fechas dentro): solo se regenera cuando cambian los casos.
- Batería: 2/2 (sin cambios en Dash).

### 2026-10-25 — Tarea 0.5 (volcado de referencia)

- `tools/volcar_lo.py`: LibreOffice por UNO (con `con_uno` de `tools/corpus.py`) abre cada `.ods`, `.fods`,
  `.xlsx`, `.odt`, `.fodt` y `.docx` del corpus y escribe `tests/ficheros/volcados/<calc|write>/<fichero>.txt`:
  hojas, celdas (tipo, valor exacto, texto mostrado, fórmula) y nombres; párrafos (estilo, alineación, sangrías,
  salto, etiqueta de lista, texto), tramos con su formato, tablas, imágenes, notas, cambios y páginas. 39 s todo,
  4 MB.
- Calc: celdas con `queryContentCells`, no recorriendo el área usada (la de `limites` es de 16.384 × 1.048.576).
- `tools/corpus.py` ahora también en inglés de EE. UU. (con español, el `.xlsx` llevaba "VERDADERO"); corpus
  regenerado.
- Lo visto, en `08` § 3.2 y § 4.3: el `.xlsx` guarda 15 cifras, los lógicos de `.xlsx` vuelven como `=TRUE()`, las
  volátiles cambian en cada volcado, los saltos de página parten tramos, imágenes en dos sitios.
- Batería: 2/2 (sin cambios en Dash).

### 2026-10-25 — Tarea 0.6, a medias (el usuario para por hoy)

Hecho:
- `tools/get_herramientas.sh` instala en `~/.cache/lorraine-tools/`: ODF Validator 0.13.0 (`.jar`), OOXML-Validator
  2.1.6 (la versión para Linux trae su propio .NET: no hace falta instalar .NET) y un `venv` con openpyxl 3.1.5 y
  python-docx 1.2.0.
- `x2t` de OnlyOffice vale en su forma simple: `x2t entrada.docx salida.odt` (desde su carpeta), sin XML de
  parámetros.
- `tools/comprobar.py`: zip, XML bien formado, validador, LibreOffice (su volcado es la referencia), OnlyOffice
  (convierte al otro formato y se compara el volcado) y openpyxl/python-docx (se comparan valores y textos).
  `tools/volcar_lo.py` tiene ahora `volcar(rutas)` para cualquier documento.
- Validador ODF: los ficheros de LibreOffice solo pasan con `-e` (sus extensiones `calcext:`/`loext:`; con `-e`
  vale también para ODF 1.4); nuestras fuentes `.fods`/`.fodt` pasan en estricto. Lorraine tendrá que pasar en
  estricto.
- Visto con el corpus: los `.docx` de LibreOffice no pasan OOXML-Validator (`w:jc val="start"`, que no es de
  Transitional); OnlyOffice convierte los errores de celda en texto (se acepta) y al pasar `texto.docx` a `.odt` se
  pierde un salto de línea (sin averiguar si al leer o al escribir); `Err:522` de una circular pasa a `#VALUE!` por
  OnlyOffice.

Por dónde seguir (siguiente iteración):
1. Revisar `build/comprobacion_corpus.txt` (la pasada de todo el corpus, 6 min; no va a git) y las 5 diferencias de
   openpyxl en `formulas.xlsx`.
2. `limites.xlsx`: openpyxl tarda más de 5 min (recorre el millón de filas). Saltarlo en la parte de Python o leer
   solo las celdas con valor (`ws._cells`).
3. Guardar en `tests/ficheros/comprobacion.txt` la línea base del corpus (qué falla ya en los ficheros de
   LibreOffice), para que luego se vea lo que es de Lorraine.
4. Marcar 0.6 `[x]` y seguir con la 0.7 (tests de funciones de LibreOffice).

