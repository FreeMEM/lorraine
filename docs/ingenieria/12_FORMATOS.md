# 12. Formatos de fichero

Qué se lee y qué se escribe de cada formato, cómo se pasa al modelo de [05](05_MODELO_DE_DATOS.md) y qué se apunta
como pérdida. **Escrito antes del código** (2026-10-24), de memoria de las especificaciones. Lo marcado
**comprobar** hay que verificarlo con la especificación o con un fichero real antes de programarlo. La prueba final
siempre es la de [08](08_PLAN_DE_PRUEBAS.md): lo que escribe Lorraine lo abre LibreOffice igual y pasa los
validadores (RNF-05).

## 1. Resumen

| Extensión | Qué es | Leer | Escribir | Hito |
|---|---|---|---|---|
| `.ods` | Hoja de cálculo ODF (ZIP) | Sí | Sí | H2 / H3 |
| `.fods` | Hoja de cálculo ODF en un solo XML (Flat ODF) | Sí | Sí | H2 / H3 |
| `.xlsx` | Hoja de cálculo OOXML Transitional | Sí | Sí | H2 / H4 |
| `.csv` | Texto separado por comas | Sí | Sí | H2 / H4 |
| `.odt` | Texto ODF (ZIP) | Sí | Sí | H6 / H7 |
| `.fodt` | Texto ODF en un solo XML | Sí | Sí | H6 / H7 |
| `.docx` | Texto OOXML Transitional | Sí | Sí | H6 / H7 |
| `.txt` | Texto plano | Sí | Sí | H6 / H7 |
| `.xlsm`, `.docm` | Con macros | Sí, sin las macros (pérdida) | No: se guarda como `.xlsx`/`.docx` | H2 / H6 |
| OOXML Strict | Variante estricta de ISO/IEC 29500 | Si sale barato (§ 3.1) | No | H2 / H6 |
| `.xls`, `.doc` | Binarios antiguos de Office | No: se reconocen y se avisa (§ 7) | No | — |

Plantillas (`.ots`, `.ott`, `.xltx`, `.dotx`): se abren como un documento nuevo con ese contenido si el tipo MIME
o el tipo de contenido es el de plantilla; no se escriben en la 1.0.

## 2. ODF (OpenDocument)

### 2.1 Paquete

Un ZIP con:

| Entrada | Contenido |
|---|---|
| `mimetype` | El tipo MIME, sin salto de línea: `application/vnd.oasis.opendocument.spreadsheet` o `application/vnd.oasis.opendocument.text`. **Primera entrada, sin comprimir** (método 0) y sin campo extra, para que se reconozca leyendo los primeros bytes. |
| `META-INF/manifest.xml` | Lista de entradas con `manifest:full-path` y `manifest:media-type`. La entrada `/` lleva el tipo MIME del documento y `manifest:version`. Aquí aparece el cifrado (§ 7). |
| `content.xml` | Estilos automáticos del cuerpo y el cuerpo (`office:body`). |
| `styles.xml` | Estilos con nombre (`office:styles`), estilos automáticos de páginas, diseños de página y páginas maestras (`office:master-styles`). |
| `meta.xml` | Título, autor, fechas (`dc:title`, `meta:initial-creator`, `dc:creator`, `meta:creation-date`, `dc:date`). RF-N15. |
| `settings.xml` | Ajustes de la vista. Calc guarda aquí filas y columnas inmovilizadas (**comprobar**: `HorizontalSplitMode`, `VerticalSplitMode` = 2 y sus posiciones, por hoja). |
| `Pictures/...` | Imágenes. |
| `Thumbnails/thumbnail.png` | Miniatura. No se lee; no se escribe en la 1.0. |

Lorraine escribe `mimetype`, `META-INF/manifest.xml`, `content.xml`, `styles.xml`, `meta.xml`, `settings.xml` (solo
si hace falta) y las imágenes.

**Espacios de nombres** que se leen (el lector los traduce a su prefijo fijo, sea cual sea el del fichero):

| Prefijo | URI |
|---|---|
| `office` | `urn:oasis:names:tc:opendocument:xmlns:office:1.0` |
| `table` | `urn:oasis:names:tc:opendocument:xmlns:table:1.0` |
| `text` | `urn:oasis:names:tc:opendocument:xmlns:text:1.0` |
| `style` | `urn:oasis:names:tc:opendocument:xmlns:style:1.0` |
| `fo` | `urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0` |
| `number` | `urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0` |
| `draw` | `urn:oasis:names:tc:opendocument:xmlns:drawing:1.0` |
| `svg` | `urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0` |
| `meta` | `urn:oasis:names:tc:opendocument:xmlns:meta:1.0` |
| `manifest` | `urn:oasis:names:tc:opendocument:xmlns:manifest:1.0` |
| `of` | `urn:oasis:names:tc:opendocument:xmlns:of:1.2` |
| `dc` | `http://purl.org/dc/elements/1.1/` |
| `xlink` | `http://www.w3.org/1999/xlink` |
| `calcext`, `loext` | Extensiones de LibreOffice (`urn:org:documentfoundation:names:experimental:...`). Se leen las pocas que hagan falta (§ 3.7); el resto se salta. |

### 2.2 Versiones

- **Se lee:** ODF 1.0 a 1.3, y 1.4 en lo que coincida. ODF 1.2 es ISO/IEC 26300:2015; 1.3 es estándar OASIS desde
  2021. **Comprobar** el estado de ODF 1.4 y qué versión escribe por defecto el LibreOffice del PC de pruebas
  ("1.3 ampliado" o "1.4 ampliado").
- **Se escribe:** ODF 1.3 sin extensiones (`office:version="1.3"`), para que pase el validador en modo estricto.
- Los ficheros de OpenOffice antiguos escriben las fórmulas con `oooc:` en vez de `of:` (§ 2.6).

### 2.3 Flat ODF (`.fods`, `.fodt`)

Un solo XML con raíz `office:document` y el atributo `office:mimetype`. Dentro van, en este orden, `office:meta`,
`office:settings`, `office:font-face-decls`, `office:styles`, `office:automatic-styles`, `office:master-styles` y
`office:body`. Las imágenes van dentro en base64 (`office:binary-data`). Sin ZIP: es el formato más fácil y por eso
es el primero que se prueba en H2 y H6.

### 2.4 Orden de lectura

1. `META-INF/manifest.xml` (¿cifrado?) y `mimetype`.
2. `styles.xml`: estilos con nombre, formatos de número, diseños de página.
3. `content.xml`: primero sus estilos automáticos, luego el cuerpo. Como los estilos van antes que el cuerpo, se
   puede leer a eventos sin volver atrás.
4. `meta.xml` y `settings.xml`.

### 2.5 Celdas en `.ods`

```xml
<table:table table:name="Hoja1">
  <table:table-column table:style-name="co1" table:number-columns-repeated="3"/>
  <table:table-row table:style-name="ro1">
    <table:table-cell office:value-type="float" office:value="1234.5" table:style-name="ce1">
      <text:p>1.234,50</text:p>
    </table:table-cell>
    <table:table-cell table:formula="of:=SUM([.A1:.A3])" office:value-type="float" office:value="6"/>
    <table:table-cell table:number-columns-repeated="16380"/>
  </table:table-row>
  <table:table-row table:number-rows-repeated="1048570"><table:table-cell table:number-columns-repeated="16384"/></table:table-row>
</table:table>
```

| `office:value-type` | Dónde está el valor | Modelo |
|---|---|---|
| `float` | `office:value` | `T_NUMERO` |
| `percentage` | `office:value` (0,25 para 25 %) | `T_NUMERO` con formato de porcentaje |
| `currency` | `office:value` y `office:currency` (`EUR`) | `T_NUMERO` con formato de moneda |
| `date` | `office:date-value` (`2026-10-24` o `2026-10-24T13:05:00`) | `T_NUMERO`, serie de fecha |
| `time` | `office:time-value` (`PT13H05M00S`) | `T_NUMERO`, fracción de día |
| `boolean` | `office:boolean-value` (`true`, `false`) | `T_LOGICO` |
| `string` | El texto de los `text:p` (o `office:string-value` si está) | `T_TEXTO` |
| (ninguno) | Celda vacía | nada |

- **Repeticiones.** `table:number-columns-repeated` en celdas y columnas, `table:number-rows-repeated` en filas.
  **Una repetición vacía no crea nada**: LibreOffice escribe filas y celdas vacías repetidas hasta el final de la
  hoja. Una repetición con contenido sí crea cada celda (comparten estilo y, si tienen fórmula, `Formula`).
- **Celdas combinadas:** `table:number-columns-spanned` y `table:number-rows-spanned` en la primera; las tapadas son
  `table:covered-table-cell`.
- **Varios párrafos** en una celda (`text:p` seguidos): se juntan con un salto de línea.
- **Texto con formato dentro de una celda** (`text:span`): se guarda el texto; el formato parcial es pérdida
  (`texto_rico_celda`).
- **Anchos:** `table:table-column` lleva un estilo con `style:column-width` (§ 5). **Altos:** el estilo de fila con
  `style:row-height`; `style:use-optimal-row-height="true"` = alto automático.
- **Ocultas:** `table:visibility="collapse"` en columnas y filas.
- **Nombres definidos:** `table:named-expressions` con `table:named-range` (`table:cell-range-address`, sin corchetes,
  p. ej. `$Hoja1.$A$1:.$B$2`) y `table:named-expression` (`table:expression="of:=..."`). **Comprobar** la sintaxis
  exacta con un fichero de LibreOffice.

Al escribir, Lorraine agrupa con repeticiones las celdas y filas vacías iguales, y no escribe las vacías del final.

### 2.6 Fórmulas (OpenFormula)

`table:formula="of:=SUM([.A1:.B3];2)"`. Reglas que cambian respecto a lo que ve el usuario:

| Cosa | OpenFormula | Excel / usuario en inglés |
|---|---|---|
| Prefijo | `of:=` (OpenOffice antiguo: `oooc:=`, con otra sintaxis; **comprobar** si merece la pena leerlo) | `=` |
| Referencia | `[.A1]` | `A1` |
| Absoluta | `[.$A$1]` | `$A$1` |
| Otra hoja | `[$Hoja2.A1]` o `[$'Mi hoja'.A1]` | `Hoja2!A1`, `'Mi hoja'!A1` |
| Rango | `[.A1:.B3]`; entre hojas `[$Hoja1.A1:$Hoja3.B3]` (3D: pérdida, compila a `#REF!`) | `A1:B3` |
| Separador de argumentos | `;` | `,` |
| Unión / intersección | `~` / `!` | `,` entre paréntesis / espacio |
| Lógicos | `TRUE()` y `FALSE()` (**comprobar**: así los escribe LibreOffice) | `TRUE`, `FALSE` |
| Errores | `#DIV/0!`, `#N/A`... | igual |

**Nombres de función.** Los de OpenFormula son los ingleses (`SUM`, `VLOOKUP`). Las funciones que no están en
OpenFormula llevan un prefijo de dominio. **Comprobar** con LibreOffice, guardando un libro que use cada una:
`COM.MICROSOFT.IFS`, `COM.MICROSOFT.SWITCH`, `COM.MICROSOFT.XLOOKUP`, `COM.MICROSOFT.TEXTJOIN`,
`COM.MICROSOFT.CONCAT` y las `ORG.OPENOFFICE.*`. La tabla de `calc/funciones.dash` lleva el nombre exacto de cada una
en cada formato ([07](07_MODULOS_E_INTERFACES.md)).

### 2.7 Estilos y formatos de número

- **Celdas:** `style:style style:family="table-cell"` (automático en `content.xml`, o con nombre en `styles.xml` con
  `style:parent-style-name`):
  - `style:text-properties`: `style:font-name`, `fo:font-size`, `fo:font-weight="bold"`, `fo:font-style="italic"`,
    `style:text-underline-style="solid"`, `style:text-line-through-style="solid"`, `fo:color`.
  - `style:table-cell-properties`: `fo:background-color`, `fo:border` y `fo:border-top/-bottom/-left/-right`
    (`0.06pt solid #000000`), `style:vertical-align`, `fo:wrap-option="wrap"`.
  - `style:paragraph-properties`: `fo:text-align` (`start`, `center`, `end`, `justify`), `fo:margin-left` (sangría).
  - `style:data-style-name`: el formato de número.
- **Formatos de número:** elementos `number:number-style`, `number:percentage-style`, `number:currency-style`,
  `number:date-style`, `number:time-style`, `number:boolean-style`, `number:text-style`. Dentro, piezas:
  `number:number` (`number:decimal-places`, `number:min-integer-digits`, `number:grouping`),
  `number:scientific-number`, `number:fraction`, `number:currency-symbol`, `number:day`, `number:month`
  (`number:style="long"`, `number:textual`), `number:year`, `number:hours`, `number:minutes`, `number:seconds`,
  `number:am-pm`, `number:text`. Las condiciones (negativos en rojo) van con `style:map` a otro estilo.
  - **Al leer**, cada estilo se traduce a un código de formato tipo Excel (`#,##0.00;[RED]-#,##0.00`) para
    `core/numeros`. Así el modelo tiene una sola forma de formato.
  - **Al escribir**, el código se vuelve a partir en piezas `number:*`. Lo que no se pueda expresar se escribe lo más
    parecido y se apunta (`formato_numero`).
- `loext:` y `calcext:` en estilos (temas, formatos condicionales de LibreOffice): se saltan; los condicionales son
  pérdida.

### 2.8 Texto en `.odt`

| Elemento | Modelo |
|---|---|
| `text:p` (`text:style-name`) | `Parrafo` con su estilo. Si el estilo es automático, su padre con nombre va a `estilo` y sus propiedades a `directo`. |
| `text:h` (`text:outline-level`) | `Parrafo` con el estilo de título de ese nivel. |
| `text:span` (`text:style-name`) | `Tramo` con formato directo (estilo automático) o estilo de carácter con nombre. |
| `text:s` (`text:c`), `text:tab`, `text:line-break` | Espacios, `\t`, `\n`. **Ojo:** en ODF los espacios seguidos del texto se funden en uno; los que cuentan van como `text:s`. Al escribir, igual. |
| `text:soft-page-break` | Se ignora (es la paginación de quien lo guardó). |
| `fo:break-before="page"` en el estilo del párrafo | `Parrafo.salto_pagina`. |
| `style:master-page-name` en el estilo del párrafo | Empieza una `Seccion` nueva con esa página maestra. |
| `text:list` / `text:list-item` (`text:style-name` con `text:list-style`) | `Parrafo.lista` y `nivel` (nivel = anidamiento de `text:list`). |
| `text:list-level-style-number` (`style:num-format` = `1`, `a`, `A`, `i`, `I`; `style:num-suffix`, `style:num-prefix`, `text:display-levels`) / `text:list-level-style-bullet` (`text:bullet-char`) | `NivelLista`. |
| `table:table` y compañía (como en § 2.5, celdas con `text:p`) | `Tabla`. `table:table-header-rows` = filas de cabecera. |
| `draw:frame` con `text:anchor-type="as-char"` y `draw:image xlink:href="Pictures/..."`; tamaño en `svg:width`, `svg:height` | Imagen en línea (U+FFFC en el texto + `Tramo.imagen`). Otros anclajes: se pone en línea y se apunta (`imagen_flotante`). |
| `style:page-layout` (`fo:page-width`, `fo:page-height`, `style:print-orientation`, `fo:margin-*`) y `style:master-page` con `style:header` / `style:footer` | `Seccion`. |
| `text:page-number` | Campo de número de página (en cabecera y pie). |
| `text:section` | Es otra cosa en ODF (zonas con columnas): se lee su contenido y se apunta si tiene columnas (`columnas`). |

Estilos de texto: `style:family="paragraph"` y `"text"`, con `style:parent-style-name` (herencia) y
`style:next-style-name`. Propiedades en `style:paragraph-properties` (`fo:text-align`, `fo:margin-left`,
`fo:margin-right`, `fo:text-indent`, `fo:margin-top`, `fo:margin-bottom`, `fo:line-height` en % o longitud,
`style:line-height-at-least`, `style:tab-stops`, `fo:keep-with-next`) y `style:text-properties` (además de las de
§ 2.7: `style:text-position="super 58%"`, `fo:background-color` para el resaltado).

## 3. OOXML: hojas de cálculo (`.xlsx`)

### 3.1 Transitional y Strict

ISO/IEC 29500 tiene dos variantes. Office escribe **Transitional** por defecto y es la que se lee y se escribe.
**Strict** cambia sobre todo las URIs de los espacios de nombres:

| | Transitional | Strict |
|---|---|---|
| SpreadsheetML | `http://schemas.openxmlformats.org/spreadsheetml/2006/main` | `http://purl.oclc.org/ooxml/spreadsheetml/main` |
| WordprocessingML | `http://schemas.openxmlformats.org/wordprocessingml/2006/main` | `http://purl.oclc.org/ooxml/wordprocessingml/main` |
| Relaciones (atributos `r:`) | `http://schemas.openxmlformats.org/officeDocument/2006/relationships` | `http://purl.oclc.org/ooxml/officeDocument/relationships` |
| Relaciones del paquete (`.rels`) | `http://schemas.openxmlformats.org/package/2006/relationships` | igual |

Leer Strict sale barato si el lector XML traduce las dos URIs al mismo prefijo y `paq_ooxml_principal` acepta los dos
tipos de relación `officeDocument`. Hay más diferencias (**comprobar**: fechas en ISO 8601 en vez de serie, algunos
valores de atributos). Se intenta en H2; si da guerra, Strict se reconoce y se avisa.

### 3.2 Paquete

- `[Content_Types].xml`: `Default` por extensión (`rels`, `xml`, `png`, `jpeg`) y `Override` por parte.
- `_rels/.rels`: la relación de tipo `.../officeDocument` apunta a la parte principal (`xl/workbook.xml`).
  **No se suponen rutas**: todo se sigue por las relaciones.
- Cada parte con relaciones tiene su `.rels` en la carpeta `_rels` de al lado (`xl/_rels/workbook.xml.rels`). Los
  destinos son relativos a la carpeta de la parte.
- `docProps/core.xml` (título, autor, fechas; RF-N15) y `docProps/app.xml`.

Tipos de contenido que escribe Lorraine (**comprobar** cada uno contra un fichero de Excel):

| Parte | Tipo de contenido |
|---|---|
| `xl/workbook.xml` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml` |
| `xl/worksheets/sheetN.xml` | `application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml` |
| `xl/sharedStrings.xml` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml` |
| `xl/styles.xml` | `application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml` |
| `docProps/core.xml` | `application/vnd.openxmlformats-package.core-properties+xml` |
| `docProps/app.xml` | `application/vnd.openxmlformats-officedocument.extended-properties+xml` |

`.xlsm` tiene otro tipo para el libro (`application/vnd.ms-excel.sheet.macroEnabled.main+xml`): se lee igual, las
macros son pérdida y se guarda como `.xlsx`.

### 3.3 Partes y orden de lectura

1. `_rels/.rels` → `xl/workbook.xml` y su `.rels`.
2. `workbook.xml`: hojas (`<sheet name sheetId r:id>`, en orden), `<workbookPr date1904="1">`, nombres definidos
   (`<definedName name localSheetId>Hoja1!$A$1:$B$2</definedName>`), `<calcPr>`.
3. `styles.xml`.
4. `sharedStrings.xml`: se carga directo en `Libro.textos`; los números de la tabla del fichero son los del modelo.
5. Cada hoja, en orden. Una hoja con relaciones a dibujos, gráficos, comentarios o tablas dinámicas apunta su
   pérdida (§ 6).

### 3.4 Celdas

```xml
<sheetData>
  <row r="1" ht="20" customHeight="1">
    <c r="A1" s="1"><v>1234.5</v></c>
    <c r="B1" t="s"><v>0</v></c>
    <c r="C1"><f>SUM(A1:A3)</f><v>6</v></c>
  </row>
</sheetData>
```

| `t` | Valor | Modelo |
|---|---|---|
| (ninguno) o `n` | `<v>` número | `T_NUMERO` |
| `s` | `<v>` índice en `sharedStrings` | `T_TEXTO` |
| `inlineStr` | `<is><t>...</t></is>` | `T_TEXTO` (se añade a la tabla) |
| `str` | `<v>` texto: resultado de texto de una fórmula | `T_TEXTO` con fórmula |
| `b` | `<v>` 0 o 1 | `T_LOGICO` |
| `e` | `<v>` `#DIV/0!`... | `T_ERROR` |
| `d` | `<v>` fecha ISO 8601 (raro; Strict y versiones nuevas) | `T_NUMERO`, serie |

- `r` en filas y celdas **puede faltar**: entonces la posición es la siguiente a la anterior.
- `s`: índice en `cellXfs` (§ 3.8).
- Textos con formato parcial en `sharedStrings` (`<si><r><rPr/><t/></r></si>`): se juntan los `t`; el formato
  parcial es pérdida (`texto_rico_celda`). `xml:space="preserve"` en `<t>` conserva espacios.
- **Columnas:** `<cols><col min max width customWidth hidden/></cols>` (ancho en § 5). **Filas:** `ht` en puntos,
  `hidden`. Por defecto: `<sheetFormatPr defaultRowHeight defaultColWidth baseColWidth>`.
- **Combinadas:** `<mergeCells><mergeCell ref="A1:B2"/></mergeCells>`.
- **Inmovilizar:** `<sheetViews><sheetView><pane xSplit ySplit topLeftCell state="frozen"/>`.

### 3.5 Fórmulas

- Sin `=` delante, nombres ingleses, `,` entre argumentos, referencias A1 (`Hoja2!A1`, `'Mi hoja'!$A$1`).
- **Funciones nuevas** con prefijo: `_xlfn.` (`_xlfn.IFS`, `_xlfn.XLOOKUP`, `_xlfn.CONCAT`, `_xlfn.TEXTJOIN`,
  `_xlfn.SWITCH`, `_xlfn.IFNA`...) y algunas `_xlws.` (**comprobar** la lista exacta guardando desde Excel). Al leer
  se quita el prefijo; al escribir se pone el de la tabla de funciones.
- **Fórmulas compartidas:** la primera celda lleva `<f t="shared" ref="B2:B10" si="0">A2*2</f>`; las demás,
  `<f t="shared" si="0"/>`. Cada seguidora es la fórmula de la primera desplazada. En el modelo es justo una
  `Formula` compartida (decisión A7). Al escribir, Lorraine puede escribirlas compartidas o cada una entera
  (**decidir en H4** midiendo tamaño y compatibilidad).
- **Fórmulas de matriz:** `<f t="array" ref="C1:C3">...</f>`. En la 1.0 se lee el valor guardado de cada celda y se
  conserva el texto; calcular matrices es pérdida (`formula_matriz`). **Comprobar** las matrices dinámicas de Excel
  365 (`cm` en la celda, `_xlfn._xlws.FILTER`...).
- `t="dataTable"`: pérdida (`tabla_datos`).
- Referencias estructuradas (`Tabla1[Columna]`) y libros externos (`[1]Hoja1!A1`): pérdida; la celda queda con su
  valor guardado y estado `C_SIN_FUNCION`.
- **Al escribir siempre se pone `<v>`** con el valor calculado, para que cualquier lector vea el resultado sin
  recalcular. **Comprobar** si conviene `<calcPr fullCalcOnLoad="1"/>` para que Excel recalcule al abrir.

### 3.6 Fechas

- **Sistema 1900** (por defecto): el número de serie 1 es el 1-1-1900. Excel cree, por un error heredado de Lotus
  1-2-3, que existió el **29-2-1900** (serie 60). Por eso, desde el 1-3-1900 (serie 61), serie = días desde el
  30-12-1899. Antes de esa fecha hay un día de diferencia. `core/fechas` lo reproduce para que las series coincidan
  con Excel.
- LibreOffice no tiene ese error: su día 0 es el 30-12-1899 en todo el rango, y las fechas antes del 1-3-1900 difieren
  de Excel en un día. **Comprobar** cómo pasa LibreOffice esas fechas al guardar `.xlsx`; en `.ods` no hay problema
  porque las fechas se guardan como texto ISO (`office:date-value`).
- **Sistema 1904** (`date1904="1"`, libros antiguos de Mac): serie 0 = 1-1-1904. `Libro.fecha1904`.
- Una celda es fecha porque su formato de número es de fecha (`num_es_fecha`), no por su valor.

### 3.7 Errores y referencias circulares (los dos formatos)

- En `.xlsx`, un error es `t="e"` con el texto (`#N/A`). En `.ods`, LibreOffice escribe el error como texto de la
  celda y, **comprobar**, `calcext:value-type="error"`.
- **`Err:522` (círculo)** no existe en Excel. Propuesta: en `.xlsx` se escribe la fórmula con el último valor
  calculado o `0` y Excel avisará del círculo al abrir; en `.ods`, como lo escriba LibreOffice (**comprobar**
  guardando un círculo desde LibreOffice).

### 3.8 Estilos (`styles.xml`)

- Listas: `numFmts` (formatos a medida, id desde 164), `fonts`, `fills` (las dos primeras reservadas: `none` y
  `gray125`), `borders`, `cellStyleXfs`, `cellXfs`, `cellStyles`, `dxfs` (formatos condicionales: pérdida).
- Una celda con `s="3"` usa `cellXfs[3]`: `<xf numFmtId fontId fillId borderId applyAlignment...>` con
  `<alignment horizontal vertical wrapText indent/>`. Cada `xf` se traduce a un `EstiloCelda` (deduplicado).
- Colores: `rgb="FFRRGGBB"` (ARGB), `theme="1"` con `tint` (colores del tema, en `xl/theme/theme1.xml`; **comprobar**
  cómo resolverlos: hace falta leer el tema), `indexed="64"` (paleta antigua de 64 colores), `auto="1"`.
- **Formatos predefinidos.** Los ids sin `numFmt` en el fichero son fijos:

| Id | Código | Id | Código |
|---|---|---|---|
| 0 | `General` | 18 | `h:mm AM/PM` |
| 1 | `0` | 19 | `h:mm:ss AM/PM` |
| 2 | `0.00` | 20 | `h:mm` |
| 3 | `#,##0` | 21 | `h:mm:ss` |
| 4 | `#,##0.00` | 22 | `m/d/yy h:mm` |
| 9 | `0%` | 37 | `#,##0 ;(#,##0)` |
| 10 | `0.00%` | 38 | `#,##0 ;[Red](#,##0)` |
| 11 | `0.00E+00` | 39 | `#,##0.00;(#,##0.00)` |
| 12 | `# ?/?` | 40 | `#,##0.00;[Red](#,##0.00)` |
| 13 | `# ??/??` | 45 | `mm:ss` |
| 14 | fecha corta del idioma (`mm-dd-yy` en la norma) | 46 | `[h]:mm:ss` |
| 15 | `d-mmm-yy` | 47 | `mmss.0` |
| 16 | `d-mmm` | 48 | `##0.0E+0` |
| 17 | `mmm-yy` | 49 | `@` |

  Los ids 5-8, 23-36 y 41-44 dependen del idioma y la moneda de quien abre el fichero. **Comprobar** con ficheros
  reales en español; mientras, se tratan como `General` con fecha si el id es de fecha. El id 14 se muestra con la
  fecha corta del idioma del Amiga (D19).
- Al escribir, Lorraine usa los ids predefinidos cuando el código coincide y crea `numFmt` desde 164 para el resto.

## 4. OOXML: textos (`.docx`)

### 4.1 Partes y orden de lectura

| Parte | Tipo de contenido (**comprobar**) | Qué se lee |
|---|---|---|
| `word/document.xml` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml` | El cuerpo |
| `word/styles.xml` | `...wordprocessingml.styles+xml` | `w:docDefaults` y estilos |
| `word/numbering.xml` | `...wordprocessingml.numbering+xml` | Listas |
| `word/headerN.xml`, `footerN.xml` | `...wordprocessingml.header+xml`, `...footer+xml` | Cabeceras y pies |
| `word/settings.xml` | `...wordprocessingml.settings+xml` | Poca cosa (pestañas por defecto, `w:evenAndOddHeaders`) |
| `word/theme/theme1.xml` | `application/vnd.openxmlformats-officedocument.theme+xml` | Fuentes y colores del tema (**comprobar** si hace falta) |
| `word/media/*` | por extensión | Imágenes |

Orden: relaciones → `styles.xml` → `numbering.xml` → `document.xml` → cabeceras y pies. Ojo: las propiedades de la
última sección (`w:sectPr` hijo de `w:body`) llegan **al final** del cuerpo; la maqueta espera a tener el documento
entero.

### 4.2 Párrafos y tramos

```xml
<w:p>
  <w:pPr><w:pStyle w:val="Heading1"/><w:jc w:val="center"/></w:pPr>
  <w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t xml:space="preserve">Hola </w:t></w:r>
  <w:r><w:t>mundo</w:t></w:r>
</w:p>
```

| Elemento | Modelo |
|---|---|
| `w:p` | `Parrafo` |
| `w:pPr/w:pStyle` | Estilo de párrafo (por `w:styleId`) |
| `w:jc` (`left`, `center`, `right`, `both`; leer también `start`, `end`) | Alineación (`both` = justificado) |
| `w:ind` (`w:left`, `w:right`, `w:firstLine`, `w:hanging`; leer también `w:start`, `w:end`) | Sangrías en twips |
| `w:spacing` (`w:before`, `w:after` en twips; `w:line` + `w:lineRule`: `auto` en 1/240 de línea, `exact` y `atLeast` en twips) | Espacios e interlineado |
| `w:tabs/w:tab` | Tabulaciones |
| `w:keepNext`, `w:pageBreakBefore` | `conservar_siguiente`, `salto_pagina` |
| `w:numPr` (`w:ilvl`, `w:numId`) | `lista`, `nivel` |
| `w:pPr/w:sectPr` | Fin de una sección (§ 4.5) |
| `w:r` | `Tramo` |
| `w:rPr`: `w:rStyle`, `w:rFonts` (`w:ascii`, `w:hAnsi`; los `*Theme` van al tema), `w:b`, `w:i`, `w:u w:val="single"`, `w:strike`, `w:color w:val="RRGGBB"` o `auto`, `w:sz` (medios puntos), `w:highlight` (colores con nombre), `w:shd w:fill`, `w:vertAlign` (`superscript`, `subscript`) | Formato de carácter |
| `w:t` | Texto (con `xml:space="preserve"` cuenta cada espacio) |
| `w:tab`, `w:br`, `w:br w:type="page"`, `w:cr` | `\t`, `\n`, salto de página (parte el párrafo y pone `salto_pagina` al siguiente), `\n` |
| `w:hyperlink` | Se leen sus tramos; el enlace es pérdida en la 1.0 (`enlaces`) |
| `w:fldSimple w:instr="PAGE"`; `w:fldChar` + `w:instrText` | Campo de página; otros campos: se queda el resultado guardado (entre `separate` y `end`) como texto, y se apunta (`campos`) |
| `w:sdt` | Se lee lo de `w:sdtContent` |
| `w:ins` / `w:del` | Control de cambios: se lee como aceptado (se queda lo insertado, se quita lo borrado) y se apunta (`control_cambios`) |
| `w:bookmarkStart`, `w:proofErr`, `w:lastRenderedPageBreak` | Se ignoran |

Al escribir, Lorraine pone `xml:space="preserve"` en todo `w:t` que empiece o acabe en espacio.

### 4.3 Herencia y propiedades de alternancia

- Orden: `w:docDefaults` → estilo de tabla → estilo de numeración → estilo de párrafo (por `w:basedOn`) → estilo de
  carácter → formato directo. En el modelo, como en [05](05_MODELO_DE_DATOS.md) § 4.4.
- **Propiedades de alternancia** (`w:b`, `w:i`, `w:caps`, `w:smallCaps`, `w:strike`, `w:dstrike`, `w:vanish`,
  `w:outline`, `w:shadow`, `w:emboss`, `w:imprint` y sus `*Cs`): **comprobar** en ECMA-376 parte 1 (sección de
  "toggle properties"). En los estilos no se heredan sin más: aparecer en un estilo de carácter invierte lo que dé el
  de párrafo. En el formato directo valen tal cual. `w:b` sin `w:val` es `true`; `w:val="0"` o `"false"` es `false`.
- `w:style w:type="paragraph|character|table|numbering"`, `w:styleId` (lo que referencian los demás), `w:name` (lo
  que ve el usuario), `w:basedOn`, `w:next`, `w:link` (pareja párrafo-carácter), `w:default="1"`.

### 4.4 Tablas

`w:tbl` con `w:tblPr` (`w:tblStyle`, `w:tblW`, `w:tblBorders`), `w:tblGrid/w:gridCol w:w` (anchos de la rejilla →
`Tabla.columnas`), `w:tr` (`w:trPr`: `w:trHeight`, `w:tblHeader` = fila de cabecera), `w:tc` (`w:tcPr`: `w:tcW`,
`w:gridSpan` → `abarca`, `w:vMerge` con `w:val="restart"` → `combina_v` 1, sin valor → 2, `w:shd w:fill`,
`w:tcBorders`). Cada `w:tc` tiene al menos un `w:p`: al escribir, nunca una celda sin párrafo. Anchos en `w:type`
`dxa` (twips), `pct` (cincuentavos de punto porcentual: 5000 = 100 %) o `auto`.

### 4.5 Secciones, cabeceras y pies

`w:sectPr`: `w:pgSz` (`w:w`, `w:h`, `w:orient`), `w:pgMar` (`w:top`, `w:right`, `w:bottom`, `w:left`, `w:header`,
`w:footer`, `w:gutter`), `w:headerReference` / `w:footerReference` (`w:type` = `default`, `first`, `even`; `r:id` →
`headerN.xml`, raíz `w:hdr`; `footerN.xml`, raíz `w:ftr`), `w:titlePg` (primera página distinta), `w:cols` (varias
columnas: pérdida `columnas`). Un `w:sectPr` dentro del `w:pPr` de un párrafo cierra la sección que acaba en ese
párrafo; el del `w:body` es el de la última. En la 1.0 se usa solo la cabecera y el pie `default`; `first` y `even`
son pérdida si existen (`cabeceras_especiales`).

### 4.6 Listas (`numbering.xml`)

`w:abstractNum` define los niveles (`w:lvl w:ilvl`: `w:start`, `w:numFmt` = `decimal`, `bullet`, `lowerLetter`,
`upperLetter`, `lowerRoman`, `upperRoman`...; `w:lvlText w:val="%1."`; `w:pPr/w:ind`; `w:rPr` con la fuente de la
viñeta). `w:num w:numId` apunta a un `w:abstractNumId` y puede cambiar niveles con `w:lvlOverride`. El párrafo usa el
`numId`.

Viñetas: Word suele usar la fuente Symbol con caracteres del área privada (`U+F0B7`). Se traducen a su carácter Unicode
(`U+F0B7` → `•`, `U+F0A7` (Wingdings) → `▪`; **comprobar** la tabla con ficheros reales). Al escribir, Lorraine usa
viñetas Unicode con una fuente normal.

### 4.7 Imágenes

En línea: `w:drawing/wp:inline` con `wp:extent cx cy` (EMU) y
`a:graphic/a:graphicData/pic:pic/pic:blipFill/a:blip r:embed="rId5"` → relación → `word/media/image1.png`.
Flotantes (`wp:anchor`): se ponen en línea y se apunta (`imagen_flotante`). VML antiguo (`w:pict` con
`v:imagedata r:id`): se intenta igual; si no, pérdida. Gráficos (`c:chart`) y formas (`wps:`): pérdida.

Espacios de nombres de DrawingML (**comprobar**): `a` = `http://schemas.openxmlformats.org/drawingml/2006/main`,
`wp` = `http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing`, `pic` =
`http://schemas.openxmlformats.org/drawingml/2006/picture`.

## 5. Unidades

Todo se pasa a twips al leer y se vuelve a la unidad del formato al escribir, redondeando al entero más cercano.

| Unidad | Dónde | A twips |
|---|---|---|
| Twip (`dxa`) | OOXML: sangrías, márgenes, página, tablas | × 1 |
| Medio punto | OOXML: `w:sz` (tamaño de letra) | × 10 |
| Octavo de punto | OOXML: grosor de bordes (`w:sz` de los bordes) | × 2,5 |
| Punto | OOXML hojas: alto de fila (`ht`), tamaño de letra (`sz` en `styles.xml`); ODF: `pt` | × 20 |
| EMU | DrawingML (imágenes): 914.400 por pulgada | ÷ 635 |
| Pulgada | ODF: `in` | × 1440 |
| Centímetro | ODF: `cm` | × 566,93 |
| Milímetro | ODF: `mm` | × 56,693 |
| Pica | ODF: `pc` | × 240 |
| Cincuentavo de % | OOXML: anchos `pct` | Relativo al ancho disponible |
| 1/240 de línea | OOXML: interlineado `auto` | Proporcional (se guarda como tal, no en twips) |
| Ancho de carácter | OOXML hojas: ancho de columna (`width`) | Ver abajo |

**Ancho de columna en `.xlsx`:** se mide en "caracteres": anchos del dígito más ancho de la fuente por defecto del
libro (Calibri 11 en Excel: 7 píxeles a 96 ppp), más un relleno. **Comprobar** la fórmula exacta de la norma.
Propuesta: `twips ≈ (width × 7 + 5) × 15` (15 twips por píxel a 96 ppp) al leer, y la inversa al escribir. La
diferencia de un píxel no importa; que el ancho vuelva igual tras abrir y guardar sí (prueba de ida y vuelta).

## 6. Pérdidas

Lo que la 1.0 no conserva. Se detecta, se apunta con `perdida(p, codigo)` y se avisa al guardar en el formato
original (decisión A9, RF-N06). El texto del aviso está en el catálogo.

| Código | Qué se pierde | ODF | OOXML |
|---|---|---|---|
| `grafico` | Gráficos | `draw:object` / `draw:frame` con objeto de gráfico | `xl/charts/*`, `c:chart` |
| `dibujo` | Formas, cuadros de texto | `draw:custom-shape`, `draw:rect`... en `table:shapes` o en el texto | `xl/drawings/*` sin imagen, `wps:` |
| `macros` | Macros | `Basic/`, `Scripts/` en el manifiesto | `vbaProject.bin`, tipos `macroEnabled` |
| `comentarios` | Comentarios | `office:annotation` | `xl/comments*.xml`, `w:commentReference` |
| `formato_condicional` | Formato condicional | `calcext:conditional-formats`, `style:map` en estilos de celda | `conditionalFormatting`, `dxfs` |
| `validacion` | Validación de datos | `table:content-validations` | `dataValidations` |
| `tabla_dinamica` | Tablas dinámicas | `table:data-pilot-tables` | `pivotTable*`, `pivotCache*` |
| `autofiltro` | Autofiltro (los botones; los datos quedan) | `table:database-ranges` con filtro | `autoFilter` |
| `tabla_datos` | Tablas de Excel con nombre y tablas de datos | — | `xl/tables/*`, `t="dataTable"` |
| `formula_matriz` | Cálculo de matrices (el valor queda) | `table:number-matrix-columns-spanned` | `t="array"` |
| `vinculos_externos` | Referencias a otros libros | `table:table-source`, referencias `'file:...'#` | `externalLink*` |
| `texto_rico_celda` | Formato parcial dentro de una celda | `text:span` en celdas | `<r>` en `sharedStrings` |
| `proteccion` | Protección de hoja o documento | `table:protected`, `text:protected` | `sheetProtection`, `w:documentProtection` |
| `control_cambios` | Control de cambios (se aceptan) | `text:tracked-changes` | `w:ins`, `w:del` |
| `notas` | Notas al pie y al final | `text:note` | `w:footnoteReference`, `w:endnoteReference` |
| `campos` | Campos que no son el número de página (queda su texto) | `text:date`, `text:author-name`... | `w:fldChar` / `w:fldSimple` |
| `enlaces` | Hipervínculos (queda el texto) | `text:a` | `w:hyperlink`, `<hyperlinks>` |
| `imagen_flotante` | Posición de imágenes no en línea | `text:anchor-type` ≠ `as-char` | `wp:anchor` |
| `columnas` | Varias columnas de texto | `style:columns`, `text:section` con columnas | `w:cols` |
| `cabeceras_especiales` | Cabecera de primera página o de páginas pares | `style:header-first`, `style:header-left` | `first`, `even` |
| `objetos` | Objetos incrustados (OLE, fórmulas de Math) | `draw:object` | `oleObject*`, `m:oMath` |
| `formato_numero` | Formatos de número que no se pueden escribir igual | — | — |

Detectar no es caro: son nombres de elementos y de partes que el lector ve pasar o que están en el manifiesto y en
las relaciones.

## 7. Cifrado y formatos antiguos

- **OOXML cifrado:** el fichero **no es un ZIP**. Es un fichero compuesto OLE2 (Compound File Binary) que empieza
  por `D0 CF 11 E0 A1 B1 1A E1` y lleva dentro los flujos `EncryptionInfo` y `EncryptedPackage`.
- **`.xls` y `.doc` antiguos:** empiezan por la misma firma. Llevan otros flujos (`Workbook` o `Book`,
  `WordDocument`).
- Para distinguirlos hay que leer el directorio del fichero compuesto (sectores de 512 bytes, la FAT y la cadena del
  directorio). Propuesta: leerlo en `core/paquete` (unas 100 líneas) y dar un aviso u otro: "documento protegido con
  contraseña" o "formato antiguo de Office: guárdalo como .xlsx o .docx en el PC". Si sale caro, un aviso único para
  los dos.
- **ODF cifrado:** el paquete es normal y `mimetype` se lee, pero en `META-INF/manifest.xml` las entradas llevan
  `manifest:encryption-data` (algoritmo, derivación de clave). Se avisa y no se abre. **Comprobar** el cifrado con
  OpenPGP de ODF 1.3 (otro esquema; **comprobar** cómo se reconoce).
- **ZIP con cifrado propio del ZIP** (bit 0 de las banderas): no se da en estos formatos; se trata como fichero
  dañado.

## 8. CSV y texto plano

**CSV** (RFC 4180 y lo que se ve en la práctica):

- Separador: `,`, `;` o tabulador. Al abrir sin opciones se adivina contando en las primeras líneas.
- Comillas: `"`, con `""` dentro. Un campo entre comillas puede tener saltos de línea.
- Fin de línea: CRLF, LF o CR.
- Codificación: UTF-8 (con o sin BOM `EF BB BF`) si es UTF-8 válido; si no, Windows-1252 (Latin-1 más `€` y comillas
  tipográficas en 0x80-0x9F).
- Valores: cada campo pasa por el mismo reconocimiento que lo que escribe el usuario (`fc_entrada`), con los
  separadores elegidos. Una opción permite leerlo todo como texto.
- Al guardar (RF-C04): por defecto, en español, `;` como separador y coma decimal (lo que espera Excel en español);
  en inglés, `,` y punto. UTF-8 con BOM o Windows-1252, a elegir. Los valores salen como se ven o sin formato, a
  elegir.

**Texto plano:** UTF-8 (con o sin BOM) si es válido; si no, Latin-1. Un párrafo por línea. Al guardar, UTF-8 o
Latin-1 (RF-W03) con LF.

## 9. Correspondencia

### 9.1 Calc

| Modelo | ODF | OOXML |
|---|---|---|
| `Libro.hojas` | `table:table` (`table:name`) | `<sheet name>` en `workbook.xml` + `sheetN.xml` |
| Celda número | `office:value-type="float"` + `office:value` | `<c><v>` |
| Celda texto | `office:value-type="string"` + `text:p` | `<c t="s">` + `sharedStrings` |
| Celda lógico | `office:value-type="boolean"` + `office:boolean-value` | `<c t="b">` |
| Celda error | texto del error (**comprobar** `calcext:value-type`) | `<c t="e">` |
| Fecha | `office:value-type="date"` + `office:date-value` (ISO) | número de serie + formato de fecha |
| `Formula` | `table:formula="of:=..."` | `<f>` (compartidas: `t="shared"`) |
| Valor guardado de la fórmula | `office:value` de la misma celda | `<v>` |
| `EstiloCelda` | `style:style family="table-cell"` | `cellXfs/xf` + `fonts`, `fills`, `borders` |
| Formato de número | `number:*-style` | `numFmtId` + `numFmts` |
| `Hoja.anchos` | `table:table-column` + `style:column-width` | `<col width>` |
| `Hoja.altos` | estilo de fila + `style:row-height` | `<row ht>` |
| Oculta | `table:visibility="collapse"` | `hidden="1"` |
| `Hoja.combinadas` | `table:number-*-spanned` + `covered-table-cell` | `<mergeCell ref>` |
| Inmovilizar | `settings.xml` (**comprobar**) | `<pane state="frozen">` |
| `NombreDefinido` | `table:named-range` / `table:named-expression` | `<definedName>` |
| `Libro.fecha1904` | `table:null-date` en `table:calculation-settings` (**comprobar**) | `<workbookPr date1904>` |

### 9.2 Write

| Modelo | ODF | OOXML |
|---|---|---|
| `Parrafo` | `text:p` / `text:h` | `w:p` |
| `Tramo` | `text:span` (o texto directo en `text:p`) | `w:r` + `w:t` |
| `EstiloParrafo` | `style:style family="paragraph"` | `w:style w:type="paragraph"` |
| `EstiloCaracter` con nombre | `style:style family="text"` con nombre | `w:style w:type="character"` |
| Formato directo de carácter | estilo automático `family="text"` | `w:rPr` del `w:r` |
| Formato directo de párrafo | estilo automático `family="paragraph"` | `w:pPr` del `w:p` |
| Negrita / cursiva | `fo:font-weight="bold"` / `fo:font-style="italic"` | `w:b` / `w:i` |
| Subrayado / tachado | `style:text-underline-style` / `style:text-line-through-style` | `w:u` / `w:strike` |
| Tamaño | `fo:font-size="12pt"` | `w:sz w:val="24"` |
| Color / resaltado | `fo:color` / `fo:background-color` | `w:color` / `w:highlight` o `w:shd` |
| Super / subíndice | `style:text-position` | `w:vertAlign` |
| Alineación | `fo:text-align` | `w:jc` |
| Sangrías | `fo:margin-left`, `fo:margin-right`, `fo:text-indent` | `w:ind` |
| Espacio antes / después | `fo:margin-top` / `fo:margin-bottom` | `w:spacing w:before` / `w:after` |
| Interlineado | `fo:line-height`, `style:line-height-at-least` | `w:spacing w:line` + `w:lineRule` |
| Salto de página | `fo:break-before="page"` | `w:pageBreakBefore` o `w:br w:type="page"` |
| `Lista`, `NivelLista` | `text:list-style` + niveles | `w:abstractNum` + `w:num` |
| `Tabla` | `table:table` | `w:tbl` |
| Celda que abarca columnas | `table:number-columns-spanned` | `w:gridSpan` |
| Combinación vertical | `table:number-rows-spanned` | `w:vMerge` |
| `Imagen` en línea | `draw:frame` (`as-char`) + `draw:image` | `wp:inline` + `a:blip r:embed` |
| `Seccion` | `style:page-layout` + `style:master-page` | `w:sectPr` |
| Cabecera / pie | `style:header` / `style:footer` en la página maestra | `w:headerReference` / `w:footerReference` |

## 10. Validadores y herramientas de prueba

El detalle está en [08](08_PLAN_DE_PRUEBAS.md) § 4.4 y § 4.5. Lo que importa al escribir los filtros:

- **No hay batería oficial de conformidad** para ninguno de los dos formatos. Validar comprueba que el fichero está
  bien formado según el esquema, no que Lorraine soporte la norma entera. Cumplir las normas enteras (miles de
  páginas) no es el objetivo; se mide la cobertura con cuatro cifras ([08](08_PLAN_DE_PRUEBAS.md) § 4.5).
- **ODF:** ODF Validator del ODF Toolkit (`tdf/odftoolkit`, Apache 2, 0.13.0 de enero de 2026), un `.jar` que corre con
  el Java del PC. **Comprobar** que valida ODF 1.3 y 1.4.
- **OOXML:** OOXML-Validator (MIT), programa de consola sobre el validador del Open XML SDK de Microsoft. Necesita .NET,
  que se instala en `~/.cache` sin tocar el sistema. Validar cada parte con `xmllint --schema` contra los XSD de
  ECMA-376 queda de reserva.
- **Fórmulas y funciones:** no hay batería oficial de OpenFormula. Los tests de funciones de LibreOffice (un `.fods`
  por función, que se comprueba solo) hacen ese papel. Como son `.fods`, Lorraine los lee desde el H2.
- **Atributos de ODF:** ODFAutoTests comprueba, atributo a atributo, qué conserva un programa al abrir y guardar.
- **Cómo escribe Office de verdad:** las notas de Microsoft [MS-OI29500] y [MS-OE376] dicen en qué se aparta Office
  de la norma. Ante una duda entre la norma y lo que hace Excel o Word, gana lo que hace Office (es lo que hay en los
  ficheros), y se apunta aquí.
- **Siempre, para los dos:** `unzip -t` (el ZIP está bien), `xmllint --noout` en cada parte (XML bien formado), y la
  ida y vuelta por LibreOffice, OnlyOffice (`x2t`) y openpyxl/python-docx comparando con el volcado de
  `tools/volcar_lo.py`.
- **Excel y Word no se usan** (decisión del usuario, 2026-10-25). Es el riesgo R-05 de
  [10](10_RIESGOS_Y_PENDIENTES.md).
