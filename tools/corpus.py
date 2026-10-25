#!/usr/bin/env python3
"""Corpus propio de documentos de prueba (docs/ingenieria/08_PLAN_DE_PRUEBAS.md, sección 3.1).

Cada caso se describe aquí y se escribe como Flat ODF (.fods, .fodt) en tests/ficheros/<calc|write>/fuente/.
Después LibreOffice, sin pantalla, lo convierte al resto de formatos en tests/ficheros/<calc|write>/:
.ods, .xlsx, .csv y .fods (el .fods guardado por LibreOffice, con los valores ya calculados) para Calc;
.odt, .docx, .txt y .fodt para Write. La versión de LibreOffice queda en tests/ficheros/VERSION.

    python3 tools/corpus.py            # todo
    python3 tools/corpus.py --fuentes  # solo las fuentes, sin LibreOffice

LibreOffice corre con un perfil propio en build/lo-perfil, para no chocar con uno abierto por el usuario.
"""

import argparse
import base64
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
FICHEROS = ROOT / "tests" / "ficheros"
PERFIL = ROOT / "build" / "lo-perfil"

NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
      'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
      'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
      'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
      'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
      'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" '
      'xmlns:xlink="http://www.w3.org/1999/xlink" '
      'xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" '
      'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" '
      'xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" '
      'office:version="1.3"')


def a(v) -> str:
    return quoteattr(str(v))


# ---------------------------------------------------------------- Calc

class Hoja:
    """Una hoja: celdas por (fila, columna) desde 0, cada una un trozo de XML ya hecho."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.celdas = {}
        self.columnas = {}      # columna -> estilo de columna
        self.filas = {}         # fila -> atributos extra de la fila
        self.combinadas = {}    # (fila, col) -> (filas, columnas)

    def poner(self, fila, col, xml):
        self.celdas[(fila, col)] = xml

    def xml(self):
        ancho = max([c for _, c in self.celdas] + list(self.columnas) + [0]) + 1
        partes = [f'<table:table table:name={a(self.nombre)}>']
        for c in range(ancho):
            estilo = f' table:style-name={a(self.columnas[c])}' if c in self.columnas else ""
            partes.append(f"<table:table-column{estilo}/>")
        alto = max([f for f, _ in self.celdas] + list(self.filas) + [0]) + 1
        vacias = 0
        for f in range(alto):
            cols = sorted(c for (ff, c) in self.celdas if ff == f)
            if not cols and f not in self.filas:
                vacias += 1
                continue
            if vacias:
                partes.append(f'<table:table-row table:number-rows-repeated="{vacias}"><table:table-cell/></table:table-row>')
                vacias = 0
            partes.append(f"<table:table-row{self.filas.get(f, '')}>")
            c = 0
            for col in cols:
                if col > c:
                    partes.append(f'<table:table-cell table:number-columns-repeated="{col - c}"/>')
                partes.append(self.celdas[(f, col)])
                c = col + 1
            partes.append("</table:table-row>")
        partes.append("</table:table>")
        return "".join(partes)


def num(v, estilo=None):
    e = f" table:style-name={a(estilo)}" if estilo else ""
    return f'<table:table-cell office:value-type="float" office:value={a(repr(v))}{e}><text:p>{v}</text:p></table:table-cell>'


def txt(s, estilo=None, extra=""):
    e = f" table:style-name={a(estilo)}" if estilo else ""
    return f'<table:table-cell office:value-type="string"{e}{extra}><text:p>{escape(s)}</text:p></table:table-cell>'


def fecha(iso, estilo="fecha"):
    return (f'<table:table-cell office:value-type="date" office:date-value={a(iso)} table:style-name={a(estilo)}>'
            f'<text:p>{iso}</text:p></table:table-cell>')


def logico(v):
    return (f'<table:table-cell office:value-type="boolean" office:boolean-value="{"true" if v else "false"}">'
            f'<text:p>{"TRUE" if v else "FALSE"}</text:p></table:table-cell>')


def formula(f, estilo=None):
    """f en OpenFormula sin el prefijo: "SUM([.A1:.A3])". LibreOffice calcula el valor al abrir."""
    e = f" table:style-name={a(estilo)}" if estilo else ""
    return f'<table:table-cell table:formula={a("of:=" + f)}{e}/>'


ESTILOS_CALC = """
<office:automatic-styles>
  <number:date-style style:name="N_fecha"><number:day number:style="long"/><number:text>/</number:text><number:month number:style="long"/><number:text>/</number:text><number:year number:style="long"/></number:date-style>
  <number:date-style style:name="N_fechahora"><number:day number:style="long"/><number:text>/</number:text><number:month number:style="long"/><number:text>/</number:text><number:year number:style="long"/><number:text> </number:text><number:hours number:style="long"/><number:text>:</number:text><number:minutes number:style="long"/></number:date-style>
  <number:time-style style:name="N_hora"><number:hours number:style="long"/><number:text>:</number:text><number:minutes number:style="long"/><number:text>:</number:text><number:seconds number:style="long"/></number:time-style>
  <number:number-style style:name="N_2dec"><number:number number:decimal-places="2" number:min-decimal-places="2" number:min-integer-digits="1"/></number:number-style>
  <number:number-style style:name="N_miles"><number:number number:decimal-places="2" number:min-decimal-places="2" number:min-integer-digits="1" number:grouping="true"/></number:number-style>
  <number:percentage-style style:name="N_porc"><number:number number:decimal-places="1" number:min-decimal-places="1" number:min-integer-digits="1"/><number:text>%</number:text></number:percentage-style>
  <number:number-style style:name="N_cient"><number:scientific-number number:decimal-places="3" number:min-decimal-places="3" number:min-integer-digits="1" number:min-exponent-digits="2"/></number:number-style>
  <number:currency-style style:name="N_euro"><number:number number:decimal-places="2" number:min-decimal-places="2" number:min-integer-digits="1" number:grouping="true"/><number:text> </number:text><number:currency-symbol number:language="es" number:country="ES">€</number:currency-symbol></number:currency-style>
  <number:text-style style:name="N_texto"><number:text-content/></number:text-style>
  <number:number-style style:name="N_ceros"><number:number number:decimal-places="0" number:min-decimal-places="0" number:min-integer-digits="5"/></number:number-style>
  <style:style style:name="fecha" style:family="table-cell" style:data-style-name="N_fecha"/>
  <style:style style:name="fechahora" style:family="table-cell" style:data-style-name="N_fechahora"/>
  <style:style style:name="hora" style:family="table-cell" style:data-style-name="N_hora"/>
  <style:style style:name="dosdec" style:family="table-cell" style:data-style-name="N_2dec"/>
  <style:style style:name="miles" style:family="table-cell" style:data-style-name="N_miles"/>
  <style:style style:name="porc" style:family="table-cell" style:data-style-name="N_porc"/>
  <style:style style:name="cient" style:family="table-cell" style:data-style-name="N_cient"/>
  <style:style style:name="euro" style:family="table-cell" style:data-style-name="N_euro"/>
  <style:style style:name="comotexto" style:family="table-cell" style:data-style-name="N_texto"/>
  <style:style style:name="ceros" style:family="table-cell" style:data-style-name="N_ceros"/>
  <style:style style:name="negrita" style:family="table-cell"><style:text-properties fo:font-weight="bold"/></style:style>
  <style:style style:name="cursiva" style:family="table-cell"><style:text-properties fo:font-style="italic"/></style:style>
  <style:style style:name="subrayado" style:family="table-cell"><style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/></style:style>
  <style:style style:name="rojo" style:family="table-cell"><style:text-properties fo:color="#c00000"/></style:style>
  <style:style style:name="fondo" style:family="table-cell"><style:table-cell-properties fo:background-color="#ffe699"/></style:style>
  <style:style style:name="bordes" style:family="table-cell"><style:table-cell-properties fo:border="0.06pt solid #000000"/></style:style>
  <style:style style:name="grande" style:family="table-cell"><style:text-properties fo:font-size="16pt" style:font-name="Liberation Serif"/></style:style>
  <style:style style:name="derecha" style:family="table-cell"><style:paragraph-properties fo:text-align="end"/></style:style>
  <style:style style:name="centro" style:family="table-cell"><style:table-cell-properties style:vertical-align="middle"/><style:paragraph-properties fo:text-align="center"/></style:style>
  <style:style style:name="ajuste" style:family="table-cell"><style:table-cell-properties fo:wrap-option="wrap"/></style:style>
  <style:style style:name="col_ancha" style:family="table-column"><style:table-column-properties style:column-width="6cm"/></style:style>
  <style:style style:name="col_oculta" style:family="table-column"><style:table-column-properties style:column-width="2.258cm"/></style:style>
  <style:style style:name="fila_alta" style:family="table-row"><style:table-row-properties style:row-height="1.5cm" style:use-optimal-row-height="false"/></style:style>
</office:automatic-styles>
"""


def libro(hojas, extra="", fecha_nula=None):
    calculo = ""
    if fecha_nula:
        calculo = f'<table:calculation-settings><table:null-date table:date-value={a(fecha_nula)}/></table:calculation-settings>'
    cuerpo = calculo + "".join(h.xml() for h in hojas) + extra
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<office:document {NS} '
            f'office:mimetype="application/vnd.oasis.opendocument.spreadsheet">{ESTILOS_CALC}'
            f"<office:body><office:spreadsheet>{cuerpo}</office:spreadsheet></office:body></office:document>\n")


def calc_valores():
    h = Hoja("Valores")
    filas = [
        ("entero", num(42)), ("negativo", num(-17)), ("decimal", num(3.14159)),
        ("grande", num(1.2345678901234567e+300)), ("pequeño", num(1e-300)),
        ("quince cifras", num(123456789012345.0)), ("cero", num(0)),
        ("0,1+0,2", formula("0.1+0.2")), ("texto", txt("Málaga, año 2026")),
        ("euro", txt("Precio: 12 €")), ("otros alfabetos", txt("Ελληνικά · Русский · 日本語")),
        ("emoji", txt("Hola 😀")), ("fecha", fecha("2026-10-25")),
        ("fecha y hora", f'<table:table-cell office:value-type="date" office:date-value="2026-10-25T13:45:00" table:style-name="fechahora"><text:p>25/10/2026 13:45</text:p></table:table-cell>'),
        ("hora", '<table:table-cell office:value-type="time" office:time-value="PT08H30M15S" table:style-name="hora"><text:p>08:30:15</text:p></table:table-cell>'),
        ("lógico verdadero", logico(True)), ("lógico falso", logico(False)),
        ("error división", formula("1/0")), ("error N/A", formula("NA()")),
        ("error valor", formula('"a"+1')), ("error nombre", formula("NOEXISTE(1)")),
    ]
    for i, (nombre, celda) in enumerate(filas):
        h.poner(i, 0, txt(nombre))
        h.poner(i, 1, celda)
    # celdas vacías en medio: algo en la fila 40 y en la columna J
    h.poner(40, 0, txt("tras un hueco"))
    h.poner(40, 9, num(9))
    return libro([h])


def calc_fechas1904():
    h = Hoja("Fechas1904")
    h.poner(0, 0, txt("Sistema de fechas de 1904"))
    h.poner(1, 0, fecha("2026-10-25"))
    h.poner(2, 0, fecha("1904-01-02"))
    h.poner(3, 0, formula("[.A2]-[.A3]"))
    return libro([h], fecha_nula="1904-01-01")


def calc_limites():
    """Una celda en la última fila y la última columna de Excel (XFD1048576)."""
    xml_hoja = ('<table:table table:name="Limites"><table:table-column table:number-columns-repeated="16384"/>'
                '<table:table-row><table:table-cell office:value-type="string"><text:p>A1</text:p></table:table-cell>'
                '</table:table-row><table:table-row table:number-rows-repeated="1048574"><table:table-cell/></table:table-row>'
                '<table:table-row><table:table-cell table:number-columns-repeated="16383"/>'
                '<table:table-cell office:value-type="float" office:value="1"><text:p>1</text:p></table:table-cell>'
                '</table:table-row></table:table>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<office:document {NS} '
            f'office:mimetype="application/vnd.oasis.opendocument.spreadsheet">'
            f"<office:body><office:spreadsheet>{xml_hoja}</office:spreadsheet></office:body></office:document>\n")


# Fórmulas: una hoja por grupo de funciones (las de H3 en 01_REQUISITOS.md § 3.3), sobre unos datos en A1:A5
FORMULAS = {
    "Matematicas": ["SUM([.A1:.A5])", "PRODUCT([.A1:.A3])", "ABS(-[.A2])", "ROUND(2.567;2)", "ROUNDUP(2.561;1)",
                    "ROUNDDOWN(2.569;1)", "INT(-2.5)", "MOD(17;5)", "POWER(2;10)", "SQRT(2)", "PI()",
                    "SIGN(-3)", "TRUNC(-2.7)"],
    "Estadistica": ["AVERAGE([.A1:.A5])", "COUNT([.A1:.A7])", "COUNTA([.A1:.A7])", "COUNTBLANK([.A1:.A8])",
                    "MAX([.A1:.A5])", "MIN([.A1:.A5])"],
    "Logica": ["IF([.A1]>2;\"grande\";\"pequeño\")", "AND(TRUE();[.A1]>0)", "OR(FALSE();[.A1]<0)", "NOT(TRUE())",
               "TRUE()", "FALSE()", "IFERROR(1/0;\"error\")"],
    "Texto": ["CONCATENATE(\"Lo\";\"rraine\")", "LEFT(\"Lorraine\";3)", "RIGHT(\"Lorraine\";3)",
              "MID(\"Lorraine\";2;3)", "LEN(\"Málaga\")", "UPPER(\"ñandú\")", "LOWER(\"ÁRBOL\")",
              "TRIM(\"  dos   espacios  \")", "TEXT(1234.5;\"#,##0.00\")", "VALUE(\"42\")"],
    "Fechas": ["DATE(2026;10;25)", "YEAR(DATE(2026;10;25))", "MONTH(DATE(2026;10;25))", "DAY(DATE(2026;10;25))",
               "TODAY()", "NOW()"],
    "Busqueda": ["VLOOKUP(3;[.A1:.B5];2;0)", "HLOOKUP(\"b\";[.D1:.F2];2;0)", "INDEX([.A1:.B5];2;2)",
                 "MATCH(4;[.A1:.A5];0)"],
    "Informacion": ["ISBLANK([.A8])", "ISNUMBER([.A1])", "ISTEXT([.A6])", "ISERROR(1/0)"],
}


def calc_formulas():
    hojas = []
    for nombre, lista in FORMULAS.items():
        h = Hoja(nombre)
        for i, v in enumerate([1, 2, 3, 4, 5]):
            h.poner(i, 0, num(v))
            h.poner(i, 1, txt("abcde"[i]))
        h.poner(5, 0, txt("texto"))
        h.poner(6, 0, logico(True))
        for j, letra in enumerate("abc"):
            h.poner(0, 3 + j, txt(letra))
            h.poner(1, 3 + j, num(10 * (j + 1)))
        for i, f in enumerate(lista):
            h.poner(10 + i, 0, txt(f))
            h.poner(10 + i, 1, formula(f))
        hojas.append(h)
    # referencias: relativas, absolutas, mixtas, a otra hoja y a un nombre
    r = Hoja("Referencias")
    for i in range(5):
        r.poner(i, 0, num(i + 1))
        r.poner(i, 1, formula(f"[.A{i + 1}]*2"))
        r.poner(i, 2, formula(f"[.A{i + 1}]*[.$E$1]"))
        r.poner(i, 3, formula(f"[.$A{i + 1}]+[.A$1]"))
    r.poner(0, 4, num(10))
    r.poner(6, 0, formula("[$Matematicas.A1]+[$Matematicas.A2]"))
    r.poner(7, 0, formula("SUM(datos)"))
    # una columna de 1.000 fórmulas iguales (decisión A7)
    for i in range(1000):
        r.poner(10 + i, 5, num(i))
        r.poner(10 + i, 6, formula(f"[.F{11 + i}]*2+1"))
    # circular y volátil
    r.poner(8, 0, formula("[.A10]+1"))
    r.poner(9, 0, formula("[.A9]+1"))
    r.poner(8, 1, formula("RAND()"))
    hojas.append(r)
    nombres = ('<table:named-expressions><table:named-range table:name="datos" '
               'table:base-cell-address="$Referencias.$A$1" table:cell-range-address="$Referencias.$A$1:.$A$5"/>'
               '</table:named-expressions>')
    return libro(hojas, extra=nombres)


def calc_formato():
    h = Hoja("Formato")
    casos = [
        ("dos decimales", num(1234.5678, "dosdec")), ("miles", num(1234567.891, "miles")),
        ("porcentaje", num(0.256, "porc")), ("científico", num(123456.789, "cient")),
        ("moneda", num(1234.5, "euro")), ("como texto", txt("00123", "comotexto")),
        ("ceros a la izquierda", num(42, "ceros")), ("fecha", fecha("2026-10-25")),
        ("negrita", txt("negrita", "negrita")), ("cursiva", txt("cursiva", "cursiva")),
        ("subrayado", txt("subrayado", "subrayado")), ("color", txt("rojo", "rojo")),
        ("fondo", txt("fondo amarillo", "fondo")), ("bordes", txt("con bordes", "bordes")),
        ("fuente y tamaño", txt("Liberation Serif 16", "grande")), ("a la derecha", txt("derecha", "derecha")),
        ("centrado", txt("centro", "centro")),
        ("ajustar texto", txt("un texto largo que no cabe en el ancho de la columna y baja de línea", "ajuste")),
    ]
    for i, (nombre, celda) in enumerate(casos):
        h.poner(i, 0, txt(nombre))
        h.poner(i, 1, celda)
    h.columnas[0] = "col_ancha"
    h.columnas[3] = "col_oculta"
    h.filas[20] = ' table:style-name="fila_alta"'
    h.poner(20, 0, txt("fila alta"))
    h.filas[21] = ' table:visibility="collapse"'
    h.poner(21, 0, txt("fila oculta"))
    h.poner(22, 0, txt("combinada 2x3", extra=' table:number-rows-spanned="2" table:number-columns-spanned="3"'))
    h.poner(22, 1, '<table:covered-table-cell table:number-columns-repeated="2"/>')
    h.poner(23, 0, '<table:covered-table-cell table:number-columns-repeated="3"/>')
    xml = libro([h])
    # columna D oculta
    return xml.replace('<table:table-column table:style-name="col_oculta"/>',
                       '<table:table-column table:style-name="col_oculta" table:visibility="collapse"/>')


def calc_tamano():
    """El libro de RNF-C01: 20.000 celdas, 2.000 de ellas fórmulas."""
    h = Hoja("Datos")
    for f in range(2000):
        for c in range(9):
            h.poner(f, c, num((f * 9 + c) % 997 + 0.25) if c != 4 else txt(f"fila {f + 1}"))
        h.poner(f, 9, formula(f"SUM([.A{f + 1}:.D{f + 1}])+[.F{f + 1}]"))
    return libro([h])


# ---------------------------------------------------------------- Write

ESTILOS_WRITE = """
<office:styles>
  <style:style style:name="Standard" style:family="paragraph"><style:text-properties style:font-name="Liberation Serif" fo:font-size="12pt"/></style:style>
  <style:style style:name="Texto" style:family="paragraph" style:parent-style-name="Standard"><style:paragraph-properties fo:margin-bottom="0.25cm"/></style:style>
  <style:style style:name="Destacado" style:family="paragraph" style:parent-style-name="Texto"><style:text-properties fo:font-style="italic" fo:color="#1f4e79"/></style:style>
  <style:style style:name="Titulo1" style:display-name="Título 1" style:family="paragraph" style:parent-style-name="Standard" style:default-outline-level="1"><style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.2cm"/><style:text-properties fo:font-size="18pt" fo:font-weight="bold" style:font-name="Liberation Sans"/></style:style>
  <style:style style:name="Enfasis" style:display-name="Énfasis" style:family="text"><style:text-properties fo:font-weight="bold" fo:color="#c00000"/></style:style>
  <text:list-style style:name="Vinetas">
    <text:list-level-style-bullet text:level="1" text:bullet-char="•"><style:list-level-properties text:list-level-position-and-space-mode="label-alignment"><style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-0.6cm" fo:margin-left="1.2cm"/></style:list-level-properties></text:list-level-style-bullet>
    <text:list-level-style-bullet text:level="2" text:bullet-char="◦"><style:list-level-properties text:list-level-position-and-space-mode="label-alignment"><style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-0.6cm" fo:margin-left="1.8cm"/></style:list-level-properties></text:list-level-style-bullet>
  </text:list-style>
  <text:list-style style:name="Numeros">
    <text:list-level-style-number text:level="1" style:num-suffix="." style:num-format="1"><style:list-level-properties text:list-level-position-and-space-mode="label-alignment"><style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-0.6cm" fo:margin-left="1.2cm"/></style:list-level-properties></text:list-level-style-number>
    <text:list-level-style-number text:level="2" style:num-suffix=")" style:num-format="a"><style:list-level-properties text:list-level-position-and-space-mode="label-alignment"><style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-0.6cm" fo:margin-left="1.8cm"/></style:list-level-properties></text:list-level-style-number>
  </text:list-style>
</office:styles>
"""

AUTO_WRITE = """
<office:automatic-styles>
  <style:style style:name="T_negrita" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>
  <style:style style:name="T_cursiva" style:family="text"><style:text-properties fo:font-style="italic"/></style:style>
  <style:style style:name="T_subrayado" style:family="text"><style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/></style:style>
  <style:style style:name="T_tachado" style:family="text"><style:text-properties style:text-line-through-style="solid"/></style:style>
  <style:style style:name="T_color" style:family="text"><style:text-properties fo:color="#00b050"/></style:style>
  <style:style style:name="T_resaltado" style:family="text"><style:text-properties fo:background-color="#ffff00"/></style:style>
  <style:style style:name="T_super" style:family="text"><style:text-properties style:text-position="super 58%"/></style:style>
  <style:style style:name="T_sub" style:family="text"><style:text-properties style:text-position="sub 58%"/></style:style>
  <style:style style:name="T_fuente" style:family="text"><style:text-properties style:font-name="Liberation Mono" fo:font-size="10pt"/></style:style>
  <style:style style:name="P_centro" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:text-align="center"/></style:style>
  <style:style style:name="P_derecha" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:text-align="end"/></style:style>
  <style:style style:name="P_justificado" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:text-align="justify"/></style:style>
  <style:style style:name="P_sangria" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:margin-left="2cm" fo:margin-right="1cm" fo:text-indent="1cm"/></style:style>
  <style:style style:name="P_interlineado" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:line-height="200%" fo:margin-top="0.5cm"/></style:style>
  <style:style style:name="P_salto" style:family="paragraph" style:parent-style-name="Texto"><style:paragraph-properties fo:break-before="page"/></style:style>
  <style:style style:name="P_apaisado" style:family="paragraph" style:parent-style-name="Texto" style:master-page-name="Apaisada"/>
  <style:style style:name="P_vertical" style:family="paragraph" style:parent-style-name="Texto" style:master-page-name="Standard"/>
  <style:style style:name="Tabla" style:family="table"><style:table-properties style:width="16cm" table:align="margins"/></style:style>
  <style:style style:name="Celda" style:family="table-cell"><style:table-cell-properties fo:padding="0.1cm" fo:border="0.5pt solid #000000"/></style:style>
  <style:style style:name="Imagen" style:family="graphic"><style:graphic-properties style:wrap="none" style:vertical-pos="top" style:horizontal-pos="center"/></style:style>
  <style:page-layout style:name="pm_vertical"><style:page-layout-properties fo:page-width="21cm" fo:page-height="29.7cm" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm"/><style:header-style><style:header-footer-properties fo:min-height="0.6cm" fo:margin-bottom="0.3cm"/></style:header-style><style:footer-style><style:header-footer-properties fo:min-height="0.6cm" fo:margin-top="0.3cm"/></style:footer-style></style:page-layout>
  <style:page-layout style:name="pm_apaisado"><style:page-layout-properties fo:page-width="29.7cm" fo:page-height="21cm" style:print-orientation="landscape" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm"/></style:page-layout>
</office:automatic-styles>
<office:master-styles>
  <style:master-page style:name="Standard" style:page-layout-name="pm_vertical">
    <style:header><text:p text:style-name="P_derecha">Lorraine · corpus de pruebas</text:p></style:header>
    <style:footer><text:p text:style-name="P_centro">Página <text:page-number text:select-page="current"/></text:p></style:footer>
  </style:master-page>
  <style:master-page style:name="Apaisada" style:page-layout-name="pm_apaisado"/>
</office:master-styles>
"""


def documento(cuerpo):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<office:document {NS} '
            f'office:mimetype="application/vnd.oasis.opendocument.text">{ESTILOS_WRITE}{AUTO_WRITE}'
            f"<office:body><office:text>{cuerpo}</office:text></office:body></office:document>\n")


def p(texto, estilo="Texto"):
    return f'<text:p text:style-name={a(estilo)}>{texto}</text:p>'


def span(texto, estilo):
    return f'<text:span text:style-name={a(estilo)}>{escape(texto)}</text:span>'


def write_texto():
    c = [
        '<text:h text:style-name="Titulo1" text:outline-level="1">Texto y formato</text:h>',
        p("Párrafo normal con acentos: árbol, camión, pingüino, ñandú. El precio es 12 €."),
        p("Otros alfabetos: Ελληνικά, Русский, 日本語, y un emoji 😀."),
        p("Tramos: " + span("negrita", "T_negrita") + ", " + span("cursiva", "T_cursiva") + ", " +
          span("subrayado", "T_subrayado") + ", " + span("tachado", "T_tachado") + ", " + span("color", "T_color") +
          ", " + span("resaltado", "T_resaltado") + ", x" + span("2", "T_super") + ", H" + span("2", "T_sub") +
          "O, " + span("monoespaciada 10 pt", "T_fuente") + " y " + span("estilo de carácter Énfasis", "Enfasis") + "."),
        p("Centrado.", "P_centro"),
        p("A la derecha.", "P_derecha"),
        p("Justificado: " + "un texto lo bastante largo para ocupar varias líneas y que se vea cómo se reparte el "
          "espacio entre las palabras de cada línea menos la última. " * 2, "P_justificado"),
        p("Con sangría izquierda de 2 cm, derecha de 1 cm y primera línea de 1 cm. " * 2, "P_sangria"),
        p("Interlineado doble y 0,5 cm de espacio antes. " * 3, "P_interlineado"),
        p("Párrafo con el estilo Destacado, que hereda de Texto, que hereda de Standard.", "Destacado"),
        p("Una línea<text:line-break/>partida con un salto de línea y<text:tab/>un tabulador."),
    ]
    return documento("".join(c))


def png(ancho, alto):
    """Un PNG de colores (degradado) hecho a mano: sin librerías."""
    filas = b"".join(b"\x00" + bytes(v for x in range(ancho) for v in (x * 255 // ancho, y * 255 // alto, 128))
                     for y in range(alto))

    def trozo(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))
    return (b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)) +
            trozo(b"IDAT", zlib.compress(filas, 9)) + trozo(b"IEND", b""))


def write_estructura():
    lista = ('<text:list text:style-name="Vinetas">'
             '<text:list-item><text:p text:style-name="Texto">Primero</text:p></text:list-item>'
             '<text:list-item><text:p text:style-name="Texto">Segundo, con otro nivel</text:p>'
             '<text:list><text:list-item><text:p text:style-name="Texto">Dentro uno</text:p></text:list-item>'
             '<text:list-item><text:p text:style-name="Texto">Dentro dos</text:p></text:list-item></text:list>'
             '</text:list-item><text:list-item><text:p text:style-name="Texto">Tercero</text:p></text:list-item></text:list>')
    numerada = ('<text:list text:style-name="Numeros">'
                '<text:list-item><text:p text:style-name="Texto">Uno</text:p>'
                '<text:list><text:list-item><text:p text:style-name="Texto">Uno a</text:p></text:list-item>'
                '<text:list-item><text:p text:style-name="Texto">Uno b</text:p></text:list-item></text:list></text:list-item>'
                '<text:list-item><text:p text:style-name="Texto">Dos</text:p></text:list-item></text:list>')
    celdas = []
    for f in range(3):
        fila = []
        for c in range(3):
            if f == 0 and c == 0:
                fila.append('<table:table-cell table:style-name="Celda" table:number-columns-spanned="2" office:value-type="string">'
                            '<text:p text:style-name="Texto">Combinada 1x2</text:p></table:table-cell>')
            elif f == 0 and c == 1:
                fila.append("<table:covered-table-cell/>")
            else:
                fila.append(f'<table:table-cell table:style-name="Celda" office:value-type="string">'
                            f'<text:p text:style-name="Texto">F{f + 1} C{c + 1}</text:p></table:table-cell>')
        celdas.append("<table:table-row>" + "".join(fila) + "</table:table-row>")
    tabla = ('<table:table table:name="Tabla1" table:style-name="Tabla"><table:table-column table:number-columns-repeated="3"/>'
             + "".join(celdas) + "</table:table>")
    imagen = ('<text:p text:style-name="Texto"><draw:frame draw:style-name="Imagen" draw:name="Imagen1" '
              'text:anchor-type="as-char" svg:width="4cm" svg:height="3cm"><draw:image><office:binary-data>'
              + base64.b64encode(png(64, 48)).decode() + '</office:binary-data></draw:image></draw:frame> imagen PNG en línea.</text:p>')
    c = [
        '<text:h text:style-name="Titulo1" text:outline-level="1">Estructura</text:h>',
        p("Lista con viñetas:"), lista, p("Lista numerada:"), numerada,
        p("Tabla con una celda combinada:"), tabla, imagen,
        p("Este párrafo empieza en una página nueva.", "P_salto"),
        p("Y este, en una página apaisada (otra sección).", "P_apaisado"),
        p("De vuelta a la página vertical.", "P_vertical"),
    ]
    return documento("".join(c))


PALABRAS = ("la suite ofimática lee y escribe documentos con cuidado para que nada se pierda al guardar en el "
            "formato de origen ni al pasar de uno a otro mientras el amiga sigue trabajando").split()


def write_tamano():
    """El documento de RNF-W01: unas 50 páginas de texto con títulos."""
    c = []
    n = 0
    for capitulo in range(1, 11):
        c.append(f'<text:h text:style-name="Titulo1" text:outline-level="1">Capítulo {capitulo}</text:h>')
        for _ in range(46):
            palabras = [PALABRAS[(n * 7 + k * 3) % len(PALABRAS)] for k in range(60 + n % 40)]
            n += 1
            c.append(p(" ".join(palabras).capitalize() + ".", "P_justificado" if n % 3 == 0 else "Texto"))
    return documento("".join(c))


# ---------------------------------------------------------------- todo

CASOS = {
    "calc": {"valores": calc_valores, "fechas1904": calc_fechas1904, "limites": calc_limites,
             "formulas": calc_formulas, "formato": calc_formato, "tamano_20k": calc_tamano},
    "write": {"texto": write_texto, "estructura": write_estructura, "tamano_50p": write_tamano},
}
CONVERSIONES = {"calc": ["ods", "xlsx", "csv", "fods"], "write": ["odt", "docx", "txt", "fodt"]}


def soffice(*args):
    PERFIL.mkdir(parents=True, exist_ok=True)
    cmd = ["soffice", f"-env:UserInstallation=file://{PERFIL}", "--headless", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        sys.exit("soffice falló: " + r.stdout + r.stderr)
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fuentes", action="store_true", help="solo las fuentes .fods/.fodt")
    args = ap.parse_args()
    for programa, casos in CASOS.items():
        fuente = FICHEROS / programa / "fuente"
        if fuente.exists():
            shutil.rmtree(fuente)
        fuente.mkdir(parents=True)
        ext = "fods" if programa == "calc" else "fodt"
        for nombre, hacer in casos.items():
            (fuente / f"{nombre}.{ext}").write_text(hacer(), encoding="utf-8")
        print(f"{programa}: {len(casos)} fuentes")
    if args.fuentes:
        return
    for programa, formatos in CONVERSIONES.items():
        salida = FICHEROS / programa
        for f in salida.iterdir():
            if f.is_file():
                f.unlink()
        fuentes = sorted(str(f) for f in (salida / "fuente").iterdir())
        for formato in formatos:
            filtro = formato
            if formato == "csv":
                # UTF-8, coma, comillas en los textos; solo la primera hoja (lo normal de un CSV)
                filtro = 'csv:Text - txt - csv (StarCalc):44,34,76,1'
            elif formato == "txt":
                filtro = "txt:Text (encoded):UTF8"
            # (limites tiene algo en XFD1048576: su CSV serían 16 GB de comas)
            lista = [f for f in fuentes if not (formato == "csv" and "limites" in f)]
            soffice("--convert-to", filtro, "--outdir", str(salida), *lista)
        print(f"{programa}: {len(list(salida.glob('*.*')))} ficheros convertidos")
    version = soffice("--version").strip()
    (FICHEROS / "VERSION").write_text(version + "\n")
    print(version)


if __name__ == "__main__":
    main()
