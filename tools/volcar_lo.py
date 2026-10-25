#!/usr/bin/env python3
"""Volcado de referencia de los documentos del corpus, leídos por LibreOffice (08_PLAN_DE_PRUEBAS.md § 3.2).

Para cada .ods, .fods, .xlsx, .odt, .fodt y .docx de tests/ficheros/<calc|write>/ escribe
tests/ficheros/volcados/<calc|write>/<fichero>.txt. Lorraine escribirá el mismo volcado desde sus tests y
tools/comparar.py comparará los dos.

    python3 tools/volcar_lo.py               # todo el corpus
    python3 tools/volcar_lo.py valores.xlsx  # uno (o varios), con su ruta o solo el nombre

LibreOffice corre con el idioma en-US (el texto mostrado de un número depende del idioma) y el perfil de
build/lo-perfil, como tools/corpus.py.

Formato, una cosa por línea y los campos separados por tabuladores (\\t, \\n y \\ dentro de un campo van escapados):

  Calc:  hoja <nombre> <filas usadas> <columnas usadas> <gráficos>
         celda <hoja>!<A1> <tipo> <valor> <mostrado> <fórmula>
            tipo: num | txt | err (valor: el código, #DIV/0!...) ; un número va con repr de Python (el más corto que
            vuelve al mismo Double), una fecha es su número de serie; fórmula: la de LibreOffice ("=SUM(A1:A5)"), o "".
         nombre <nombre> <contenido>
  Write: parrafo <estilo> <alineación> <sangría izq.> <der.> <primera línea> <salto> <etiqueta de lista> <texto>
            (sangrías en centésimas de mm, como UNO; salto: page si empieza página)
         tramo <texto> <formato>   formato: fuente tamaño y marcas n (negrita) c (cursiva) s (subrayado) t (tachado)
            sup / sub, color=#rrggbb, fondo=#rrggbb, estilo=<de carácter>
         tabla <nombre> <filas> <columnas> ; fila <celda> | <celda> ...
         imagen <nombre> <ancho> <alto>   (centésimas de mm)
         notas <al pie> <al final> ; cambios <número> ; paginas <número>
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402  (con_uno, prop, rutas)

FICHEROS = corpus.FICHEROS
SALIDA = FICHEROS / "volcados"
EXTENSIONES = {"calc": ("ods", "fods", "xlsx"), "write": ("odt", "fodt", "docx")}
ERRORES = {503: "#NUM!", 504: "#VALUE!", 507: "#N/A", 519: "#VALUE!", 522: "Err:522", 523: "Err:523",
           524: "#REF!", 525: "#NAME?", 532: "#DIV/0!", 32767: "#N/A"}


def esc(s) -> str:
    return str(s).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def linea(*campos) -> str:
    return "\t".join(esc(c) for c in campos)


def columna(n: int) -> str:
    letras = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        letras = chr(65 + r) + letras
    return letras


def volcar_calc(doc):
    from com.sun.star.table.CellContentType import TEXT, FORMULA
    from com.sun.star.sheet.FormulaResult import VALUE as R_VALUE, STRING as R_STRING
    salida = []
    banderas = 1 | 2 | 4 | 16          # VALUE, DATETIME, STRING, FORMULA (CellFlags)
    for i in range(doc.Sheets.Count):
        hoja = doc.Sheets.getByIndex(i)
        cursor = hoja.createCursor()
        cursor.gotoEndOfUsedArea(False)
        fin = cursor.RangeAddress
        salida.append(linea("hoja", hoja.Name, fin.EndRow + 1, fin.EndColumn + 1, hoja.Charts.Count))
        celdas = []
        rangos = hoja.queryContentCells(banderas)
        enum = rangos.Cells.createEnumeration()
        while enum.hasMoreElements():
            c = enum.nextElement()
            a = c.CellAddress
            celdas.append((a.Row, a.Column, c))
        for fila, col, c in sorted(celdas, key=lambda x: (x[0], x[1])):
            ref = f"{hoja.Name}!{columna(col)}{fila + 1}"
            formula = ""
            if c.Type == FORMULA:
                formula = c.Formula
                if c.getError():
                    tipo, valor = "err", ERRORES.get(c.getError(), f"Err:{c.getError()}")
                elif c.FormulaResultType2 == R_STRING:
                    tipo, valor = "txt", c.String
                else:
                    tipo, valor = "num", repr(c.Value)
            elif c.Type == TEXT:
                tipo, valor = "txt", c.String
            else:
                tipo, valor = "num", repr(c.Value)
            salida.append(linea("celda", ref, tipo, valor, c.String, formula))
    nombres = doc.NamedRanges
    for n in sorted(nombres.ElementNames):
        salida.append(linea("nombre", n, nombres.getByName(n).Content))
    return salida


ALINEACION = {0: "izquierda", 1: "derecha", 2: "justificado", 3: "centro", 4: "justificado"}


def color(v) -> str:
    return "" if v is None or v < 0 else f"#{v & 0xFFFFFF:06x}"


def formato_tramo(t) -> str:
    from com.sun.star.awt.FontWeight import BOLD
    from com.sun.star.awt.FontSlant import ITALIC
    marcas = [f"{t.CharFontName} {t.CharHeight:g}"]
    if t.CharWeight >= BOLD:
        marcas.append("n")
    if t.CharPosture == ITALIC:
        marcas.append("c")
    if t.CharUnderline:
        marcas.append("s")
    if t.CharStrikeout:
        marcas.append("t")
    if t.CharEscapement > 0:
        marcas.append("sup")
    elif t.CharEscapement < 0:
        marcas.append("sub")
    if color(t.CharColor):
        marcas.append("color=" + color(t.CharColor))
    fondo = t.CharBackColor if t.CharBackColor >= 0 else getattr(t, "CharHighlight", -1)
    if color(fondo):
        marcas.append("fondo=" + color(fondo))
    if t.CharStyleName and t.CharStyleName not in ("Standard", "Default Character Style"):
        marcas.append("estilo=" + t.CharStyleName)
    return " ".join(marcas)


def volcar_parrafo(p, salida):
    from com.sun.star.style.BreakType import PAGE_BEFORE
    salto = "page" if p.BreakType == PAGE_BEFORE or p.PageDescName else ""
    etiqueta = p.ListLabelString if p.NumberingIsNumber else ""
    salida.append(linea("parrafo", p.ParaStyleName, ALINEACION.get(p.ParaAdjust, p.ParaAdjust), p.ParaLeftMargin,
                        p.ParaRightMargin, p.ParaFirstLineIndent, salto, etiqueta, p.String))
    # los trozos seguidos con el mismo formato van juntos (LibreOffice parte el texto donde cae un salto de
    # página suave, y eso depende de la maqueta, no del documento)
    tramos = []
    enum = p.createEnumeration()
    while enum.hasMoreElements():
        t = enum.nextElement()
        if t.TextPortionType == "Text" and t.String:
            f = formato_tramo(t)
            if tramos and tramos[-1][1] == f:
                tramos[-1][0] += t.String
            else:
                tramos.append([t.String, f])
    for texto, f in tramos:
        salida.append(linea("tramo", texto, f))


def volcar_write(doc):
    salida = []
    enum = doc.Text.createEnumeration()
    while enum.hasMoreElements():
        e = enum.nextElement()
        if e.supportsService("com.sun.star.text.Paragraph"):
            volcar_parrafo(e, salida)
        elif e.supportsService("com.sun.star.text.TextTable"):
            salida.append(linea("tabla", e.Name, e.Rows.Count, e.Columns.Count))
            for nombres in _celdas_por_fila(e):
                salida.append(linea("fila", " | ".join(e.getCellByName(n).String for n in nombres)))
    # las imágenes, de la página de dibujo: ahí están las de texto y las que LibreOffice carga como dibujo
    # (una imagen de texto está en GraphicObjects; según cómo venga del fichero puede estar solo en DrawPage)
    imagenes = {}
    for n in doc.GraphicObjects.ElementNames:
        g = doc.GraphicObjects.getByName(n)
        imagenes[n] = (g.Size.Width, g.Size.Height)
    for i in range(doc.DrawPage.Count):
        s = doc.DrawPage.getByIndex(i)
        if "GraphicObject" in s.ShapeType and s.Name not in imagenes:
            imagenes[s.Name] = (s.Size.Width, s.Size.Height)
    for n, (ancho, alto) in sorted(imagenes.items()):
        salida.append(linea("imagen", n, ancho, alto))
    notas_final = doc.Endnotes.Count if hasattr(doc, "Endnotes") else 0
    salida.append(linea("notas", doc.Footnotes.Count, notas_final))
    salida.append(linea("cambios", doc.Redlines.Count if hasattr(doc, "Redlines") else 0))
    salida.append(linea("paginas", doc.CurrentController.PageCount))
    return salida


def _celdas_por_fila(tabla):
    """Los nombres de las celdas fila a fila (una tabla con combinadas no es una rejilla: getCellNames sí vale)."""
    filas = {}
    for n in tabla.CellNames:
        letras = "".join(ch for ch in n if ch.isalpha())
        num = int("".join(ch for ch in n if ch.isdigit()))
        filas.setdefault(num, []).append((len(letras), letras, n))
    return [[n for _, _, n in sorted(v)] for _, v in sorted(filas.items())]


def ficheros(pedidos):
    todos = [(prog, f) for prog, exts in EXTENSIONES.items() for ext in exts
             for f in sorted((FICHEROS / prog).glob(f"*.{ext}"))]
    if not pedidos:
        return todos
    return [(prog, f) for prog, f in todos if any(f.name == Path(p).name for p in pedidos)]


def main():
    lista = ficheros(sys.argv[1:])
    if not lista:
        sys.exit("ningún fichero del corpus coincide")
    os.environ.update(LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8")
    version = (FICHEROS / "VERSION").read_text().split(" ")[1] if (FICHEROS / "VERSION").exists() else "?"
    version = "LibreOffice " + version

    def trabajo(desktop):
        import uno
        for prog, f in lista:
            doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(f)), "_blank", 0,
                                               (corpus.prop("Hidden", True),))
            try:
                # sin recalcular: el valor guardado de cada fórmula (decisión A8); las volátiles (RAND, NOW,
                # TODAY) las recalcula LibreOffice al abrir y cambian en cada volcado: tools/comparar.py las salta
                if prog == "calc":
                    lineas = volcar_calc(doc)
                else:
                    lineas = volcar_write(doc)
            finally:
                doc.close(True)
            destino = SALIDA / prog / f"{f.name}.txt"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(f"# {f.name} leído por {version}, en-US\n" + "\n".join(lineas) + "\n",
                               encoding="utf-8")
            print(f"{prog}/{f.name}: {len(lineas)} líneas")
    corpus.con_uno(trabajo)


if __name__ == "__main__":
    main()
