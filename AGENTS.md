# Lorraine — guía para agentes

Suite ofimática para AmigaOS 3.x con interfaz MUI, escrita en Dash (`~/Projects/FreeMEMLang`, repo FreeMEM/dash):
**Lorraine Calc** (hoja de cálculo) y **Lorraine Write** (procesador de textos). Abren y guardan ODF (`.ods`,
`.odt`) y OOXML (`.xlsx`, `.docx`). Licencia MIT. Nombre elegido por el usuario el 2026-10-24 (Lorraine: el nombre en
clave del prototipo del Amiga). Nada se llama "Amiga algo".

**Estado: diseño, sin código.** Empieza por `docs/ingenieria/00_INDICE.md` y `docs/ARQUITECTURA.md`.

Plan, reglas y bitácora: `docs/LORRAINE_LOOP.md` (sesiones largas por tandas, rama local `dev`, sin push).
Máquina mínima: A1200 con 68030 y FPU real. Interfaz: MUI siempre, nunca GadTools, ReAction ni Intuition suelta (usuario, 2026-10-25).

## Reglas

- **Lorraine existe para hacer crecer Dash.** Lo que le falte a Dash se añade a Dash (tareas `D<n>` de
  `docs/ingenieria/13_DASH.md`), sin rodeos con `@native`. C solo en `third_party/` y en su pegamento.
- **El código de Ignition (GPL v3) no se copia.** Se puede leer para entender; se escribe de nuevo.
- Solo código que se pueda redistribuir con MIT.
- Texto interno en UTF-8; números `Double`; maqueta en twips. Decisiones A1-A12 en `docs/ARQUITECTURA.md` § 8: si
  algo las contradice, se pregunta antes de cambiarlas.
- Antes de escribir Dash, lee `~/Projects/FreeMEMLang/docs/SINTAXIS.md`.

## Dash

Worktree propio: `~/Projects/FreeMEMLang/.worktrees/lorraine` (rama `lorraine`, sale de `main`; `$DASH` por
defecto). **Aún no existe**: se crea en el hito H0. Del resto de `~/Projects/FreeMEMLang` no se toca nada. Tachyon
usa otro worktree (`dashweb`): no pisarlo.

## Estructura

- `core/`: módulos compartidos (zip, XML, UTF-8, números, fechas, estilos, deshacer, fuentes, portapapeles, PDF,
  interfaz).
- `calc/`, `write/`: cada programa con su `.dash` principal, su `.dashui` y sus módulos.
- `tests/`: `run.py` y `test_*.dash` (en FS-UAE); `tests/ficheros/`: corpus de documentos.
- `third_party/`: zlib, stb_truetype. `tools/`: scripts. `catalogos/`: traducciones.

## Comandos

```bash
export DASH_KICKSTART="/home/freemem/Descargas/Telegram Desktop/ks31a1200.rom"
export DASH_EMU_SYS=~/.cache/dash-emu/sys31 DASH_EMU_SYS_MUI=~/.cache/dash-emu/sys31mui
python3 tests/run.py            # compila tests/test_*.dash (y calc/, write/) y los ejecuta en FS-UAE (A1200 + 68882)
python3 tests/run.py zip -v     # solo los que contienen "zip", con la salida de los que fallan
```

Directivas de los tests: las explica `tests/run.py`. Las capturas quedan en `build/tests/`.
