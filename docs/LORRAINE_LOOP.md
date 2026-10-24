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

- [ ] 0.1 Rama `dev` en Lorraine. Worktree de Dash `.worktrees/lorraine` (rama `lorraine` desde `main`). Dash compila
      un hola con `--fpu`.
- [ ] 0.2 `tests/run.py` (del de Tachyon, adaptado: `$DASH` por omisión el worktree `lorraine`; entornos a1200,
      a1200-mui y a1200-030) y `tests/test_hola.dash`, que pasa en FS-UAE con la ROM 3.1. Captura de una ventana MUI
      de prueba con el nombre de Lorraine.
- [ ] 0.3 Entorno "a1200-030": FS-UAE con 68030 + 68882, sin JIT, a la velocidad de una Blizzard 1230 de 50 MHz
      (averiguar las opciones; apuntar cómo se comprobó). Un bucle de referencia medido en los tres entornos.
- [ ] 0.4 `tools/corpus.py`: corpus propio con `soffice --headless` en `tests/ficheros/` (Calc: valores, fórmulas,
      formatos, varias hojas, fechas; Write: párrafos, estilos, listas, tabla, imagen), en todos los formatos.
- [ ] 0.5 `tools/volcar_lo.py`: volcado de referencia (valores de celdas, texto y formato de párrafos).
- [ ] 0.6 Herramientas de comprobación (`08` § 4.4) en `~/.cache/lorraine-tools/`: ODF Validator, .NET y
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
