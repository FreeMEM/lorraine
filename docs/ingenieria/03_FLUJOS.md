# 03. Flujos

Cómo trabajará Lorraine por dentro: diagramas de flujo y de secuencia de los procesos principales. Es el diseño de
partida, antes del código. Los módulos son los de [ARQUITECTURA](../ARQUITECTURA.md); **los nombres de funciones son
propuestas** (en español, con el prefijo de su módulo) y pueden cambiar al escribir el código. Los estados de cada
objeto están en [04](04_ESTADOS.md).

Índice:

| ID | Flujo | Tipo | Programa |
|---|---|---|---|
| F-01 | Arranque y salida | Flujo | Los dos |
| F-02 | Bucle de eventos | Flujo | Los dos |
| F-03 | Abrir un fichero | Secuencia | Los dos |
| F-04 | Detectar el formato | Flujo | Los dos |
| F-05 | Leer una entrada del ZIP a eventos XML | Flujo | Los dos |
| F-06 | Guardar seguro | Flujo | Los dos |
| F-07 | Escribir en una celda | Flujo | Calc |
| F-08 | Reconocer lo escrito | Flujo | Calc |
| F-09 | Compilar una fórmula | Flujo | Calc |
| F-10 | Recalcular | Flujo | Calc |
| F-11 | Pintar la rejilla y repintar una zona | Flujo | Calc |
| F-12 | Una tecla en Write | Secuencia | Write |
| F-13 | Repaginar | Flujo | Write |
| F-14 | Deshacer y rehacer | Flujo | Los dos |
| F-15 | Copiar | Secuencia | Los dos |
| F-16 | Pegar | Flujo | Los dos |

## F-01 Arranque y salida

Igual en los dos programas. Se muestra Calc.

```mermaid
flowchart TD
    A([LorraineCalc arranca]) --> B{"mui_app_begin == 0?"}
    B -- sí --> B1["Mensaje: necesita MUI y un 68020"] --> Z([fin])
    B -- no --> C["Abrir catálogo (tr); leer preferencias y recientes"]
    C --> D["Leer separadores del idioma (D19): decimal, miles, orden de fecha"]
    D --> E["Leer argumentos: Shell (ficheros) o Workbench (iconos)"]
    E --> F{"¿algún fichero?"}
    F -- no --> G["ventana_nueva(libro vacío)"]
    F -- sí --> H["por cada fichero: F-03 Abrir"]
    H --> I{"¿se abrió alguno?"}
    I -- no --> G
    I -- sí --> L
    G --> L[[F-02 Bucle de eventos]]
    L --> M["Salir: por cada ventana con cambios, CU-N04"]
    M --> N{"¿alguien canceló?"}
    N -- sí --> L
    N -- no --> O["Liberar cada documento; guardar preferencias y recientes; mui_app_end"]
    O --> Z
```

## F-02 Bucle de eventos

Un solo bucle con `mui_wait_event`. Cada ventana tiene su documento. Los números de evento llevan el número de la
ventana (como en Tachyon: `ID_X + k`).

```mermaid
flowchart TD
    A{"ventanas abiertas > 0"} -- no --> Z([salir])
    A -- sí --> B["ev = mui_wait_event()"]
    B --> C{"ev == -1 o ID_SALIR"}
    C -- sí --> Z
    C -- no --> D["k = ventana del evento"]
    D --> E{"tipo de evento"}
    E -- "menú u orden" --> F["orden_ejecutar(k, orden)"]
    E -- "lienzo: tecla, clic, rueda, arrastre" --> G["entrada_lienzo(k)"]
    E -- "campo de fórmula (Calc)" --> H["F-07 Escribir en una celda"]
    E -- "barra de desplazamiento" --> I["mover la vista; F-11 o pintar páginas"]
    E -- "temporizador" --> J["cursor parpadea (Write); trabajo pendiente a trozos"]
    E -- "cerrar ventana" --> K["CU-N04"]
    F --> U["ventana_al_dia(k): título con *, menús activos, barra de estado"]
    G --> U
    H --> U
    I --> A
    J --> A
    K --> A
    U --> A
```

`ventana_al_dia` pone en el título un `*` si hay cambios, activa o desactiva Deshacer, Rehacer, Pegar, Guardar, y
escribe la barra de estado. Se llama tras cada orden, no en cada repintado.

## F-03 Abrir un fichero

```mermaid
sequenceDiagram
    participant U as Usuario
    participant P as Programa (calc.dash / write.dash)
    participant PQ as core/paquete
    participant Z as core/zip
    participant X as core/xml_lector
    participant F as Filtro (ods, xlsx, odt, docx...)
    participant M as Modelo (libro / documento)

    U->>P: Proyecto › Abrir, elige fichero
    P->>PQ: paquete_detectar(ruta)
    PQ->>Z: zip_abrir(ruta) (si empieza por "PK")
    Z-->>PQ: directorio central (nombres, tamaños, posiciones)
    PQ-->>P: formato (ODS, XLSX, FODS, CSV...) o error (F-04)
    P->>M: libro_nuevo() / documento_nuevo()
    P->>F: filtro_leer(paquete, modelo)
    F->>PQ: partes en orden: estilos, luego contenido (manifest o .rels)
    loop una entrada del ZIP cada vez
        F->>Z: zip_entrada(nombre) → búfer (inflate, D6)
        F->>X: xml_empezar(búfer)
        loop hasta fin
            X-->>F: evento (inicio, atributo, texto, fin)
            F->>M: crea hoja, fila, celda, estilo, párrafo, tramo...
            F->>M: si no entiende el elemento: pérdida apuntada, salta el subárbol
        end
        F->>Z: suelta el búfer
    end
    F-->>P: bien, o error con el motivo
    alt bien
        P->>M: Calc: compila las fórmulas, guarda el valor del fichero (A8)
        P->>U: ventana con el documento, estado "sin cambios"
    else error
        P->>M: libera lo leído
        P->>U: mensaje (CU-N06)
    end
```

Notas:

- Nunca hay un árbol XML en memoria. El búfer descomprimido de una entrada sí está entero; el mayor del corpus da
  la medida de memoria del pico (ver [10](10_RIESGOS_Y_PENDIENTES.md)).
- La lista de pérdidas se guarda en el modelo con un contador por tipo ("gráficos: 2").
- Saltar un subárbol desconocido es contar profundidad: `xml_saltar()` avanza hasta el fin del elemento abierto.

## F-04 Detectar el formato

```mermaid
flowchart TD
    A["paquete_detectar(ruta)"] --> B["leer los primeros bytes"]
    B --> C{"¿empieza por PK?"}
    C -- no --> D{"¿XML con office:document?"}
    D -- sí --> D1{"office:mimetype"}
    D1 -- spreadsheet --> FODS([FODS])
    D1 -- text --> FODT([FODT])
    D -- no --> E{"¿cabecera OLE (D0 CF 11 E0)?"}
    E -- sí --> E1{"¿tiene EncryptionInfo?"}
    E1 -- sí --> CIF([error: cifrado])
    E1 -- no --> OLD([error: .xls o .doc antiguo])
    E -- no --> T{"¿parece texto?"}
    T -- sí --> TXT([CSV en Calc, TXT en Write])
    T -- no --> DESC([error: desconocido])
    C -- sí --> F["zip_abrir: directorio central"]
    F --> F0{"¿ZIP legible?"}
    F0 -- no --> DAN([error: dañado])
    F0 -- sí --> G{"¿hay entrada mimetype?"}
    G -- sí --> G1{"contenido de mimetype"}
    G1 -- "...spreadsheet" --> ODS([ODS])
    G1 -- "...text" --> ODT([ODT])
    G1 -- otro --> DESC
    G -- no --> H{"¿hay [Content_Types].xml?"}
    H -- no --> DESC
    H -- sí --> H1["_rels/.rels: parte principal y su tipo"]
    H1 -- "...sheet.main..." --> XLSX([XLSX])
    H1 -- "...document.main..." --> DOCX([DOCX])
    H1 -- otro --> DESC
```

Un ODF cifrado se reconoce en el `manifest.xml` (`manifest:encryption-data`) al leerlo, y da el mismo error que el
OOXML cifrado. Si el formato es del otro programa, el que llama da el aviso de CU-N01 3b.

## F-05 Leer una entrada del ZIP a eventos XML

```mermaid
flowchart TD
    A["zip_entrada(nombre)"] --> B{"método"}
    B -- "0: guardada" --> C["leer los bytes tal cual"]
    B -- "8: deflate" --> D["leer comprimido; inflate (D6) a un búfer del tamaño declarado"]
    B -- otro --> ERR([error: dañado])
    C --> E["crc32 (D6) == el del directorio?"]
    D --> E
    E -- no --> ERR
    E -- sí --> F["xml_empezar(búfer, largo)"]
    F --> G["xml_siguiente()"]
    G --> H{"evento"}
    H -- "inicio" --> I["nombre con prefijo fijo de Lorraine (espacios de nombres resueltos)"]
    H -- "atributo" --> J["nombre y valor, entidades ya resueltas"]
    H -- "texto" --> K["texto UTF-8 (entidades resueltas)"]
    H -- "fin" --> L["cierra el elemento"]
    H -- "fin del documento" --> M([soltar búfer])
    H -- "error" --> N([error: XML roto en línea N])
    I --> G
    J --> G
    K --> G
    L --> G
```

Propuesta para que el lector vaya rápido: los nombres de elemento y atributo se comparan con constantes por número
(una tabla de nombres conocidos que se busca una vez por nombre), no con textos en cada evento. El texto se entrega
como posición y largo dentro del búfer; solo se copia a un `String` si el filtro lo guarda.

## F-06 Guardar seguro

```mermaid
flowchart TD
    A["guardar(doc, ruta, formato)"] --> B{"¿formato == origen y hay pérdidas?"}
    B -- sí --> B1[["CU-N03: Guardar igualmente / Guardar como / Cancelar"]]
    B1 -- Cancelar --> Z0([nada])
    B1 -- "Guardar como" --> GC["diálogo de nombre"] --> A
    B1 -- "Guardar igualmente" --> C
    B -- no --> C["tmp = misma carpeta, nombre.lorraine-tmp"]
    C --> D["zip_crear(tmp) (o fichero plano en FODS, FODT, CSV, TXT)"]
    D --> E["por cada parte: xml_escritor a un búfer → zip_añadir (guardada o deflate)"]
    E --> F{"¿algún error? (disco, memoria)"}
    F -- sí --> F1["cerrar y borrar tmp"] --> F2(["mensaje: el original sigue intacto y el documento sigue con cambios"])
    F -- no --> G["zip_cerrar: directorio central"]
    G --> H{"¿existe el original?"}
    H -- sí --> H1["renombrar original a nombre.lorraine-bak"]
    H1 --> I["renombrar tmp a nombre"]
    H -- no --> I
    I --> J{"¿bien?"}
    J -- no --> J1["deshacer: .lorraine-bak vuelve a su nombre"] --> F2
    J -- sí --> K["borrar .lorraine-bak"]
    K --> L["doc: sin cambios; origen = formato; pérdidas vacías; marca de guardado en la pila de deshacer"]
    L --> Z([Guardado])
```

En AmigaOS `Rename` no reemplaza un fichero que existe; por eso el paso por `.lorraine-bak`. Se conservan, si se
puede, el comentario y los bits de protección del original (propuesta; comprobar qué da Dash).

En ODF, la entrada `mimetype` va la primera y sin comprimir; en OOXML, `[Content_Types].xml` primero. Detalle en
[12](12_FORMATOS.md).

## F-07 Escribir en una celda

```mermaid
flowchart TD
    A["Usuario teclea en una celda o en el campo de fórmula"] --> B["E-02: Escribiendo"]
    B --> C{"tecla"}
    C -- "Esc" --> C1["descartar; la celda queda como estaba"] --> Z([Navegando])
    C -- "Return, Tab, flecha (si no está señalando)" --> D["texto = lo escrito"]
    D --> E["F-08 Reconocer lo escrito"]
    E --> F{"¿error de fórmula?"}
    F -- sí --> F1["aviso; el cursor al sitio del error; sigue Escribiendo"]
    F -- no --> G["orden 'poner celda' a la pila de deshacer (valor y estilo de antes)"]
    G --> H["libro_poner(hoja, fila, col, valor o fórmula)"]
    H --> I["quitar las dependencias de la fórmula vieja; poner las de la nueva"]
    I --> J["marcar sucia la celda y lo que depende de ella"]
    J --> K["F-10 Recalcular"]
    K --> L["F-11 repintar las celdas que cambiaron"]
    L --> M["mover la celda activa (abajo, derecha...)"]
    M --> Z
```

## F-08 Reconocer lo escrito

Las reglas siguen el idioma (D19). Se muestra el español.

```mermaid
flowchart TD
    A["texto"] --> B{"vacío?"}
    B -- sí --> V0([celda vacía])
    B -- no --> C{"empieza por '='?"}
    C -- sí --> FO([F-09 Compilar fórmula])
    C -- no --> D{"empieza por apóstrofo?"}
    D -- sí --> TX([texto, sin el apóstrofo])
    D -- no --> E{"¿número con los separadores del idioma? '1.234,5', '-3', '1,5E3'"}
    E -- sí --> NUM([número])
    E -- no --> F{"¿termina en % y lo de antes es número?"}
    F -- sí --> PC(["número / 100, formato porcentaje si la celda era General"])
    F -- no --> G{"¿moneda: '12,50 €'?"}
    G -- sí --> MO(["número, formato moneda si era General"])
    G -- no --> H{"¿fecha u hora en el orden del idioma? '24/10/2026', '14:30'"}
    H -- sí --> FE(["número de serie (core/fechas), formato fecha u hora si era General"])
    H -- no --> I{"VERDADERO / FALSO (o TRUE / FALSE)?"}
    I -- sí --> LO([lógico])
    I -- no --> TX2([texto])
```

## F-09 Compilar una fórmula

```mermaid
flowchart TD
    A["texto '=SUMA(A1:B3;2)*$C$1'"] --> B["lexer: piezas (número, texto, referencia, rango, nombre, función, operador, separador)"]
    B --> B1{"¿pieza inválida?"}
    B1 -- sí --> E1([error con su posición])
    B1 -- no --> C["parser: precedencia de operadores, llamadas, rangos, hojas ('Hoja2'.A1)"]
    C --> C1{"¿error de sintaxis?"}
    C1 -- sí --> E1
    C1 -- no --> D["buscar cada función en la tabla del idioma, luego en la inglesa"]
    D --> D1{"¿existe?"}
    D1 -- no --> D2["se compila igual, con la función marcada 'desconocida' (A8, CU-C02)"]
    D1 -- sí --> F
    D2 --> F["generar código para una pila (polaca inversa), referencias relativas a la celda (R1C1)"]
    F --> G{"¿ya hay una fórmula igual en el libro?"}
    G -- sí --> H["usar esa (contador de usos +1): una columna de fórmulas copiadas gasta como una"]
    G -- no --> I["guardar en la tabla de fórmulas del libro"]
    H --> J([Formula + lista de celdas y rangos que lee])
    I --> J
```

El mismo compilador lee las fórmulas de los ficheros con otra tabla de lexer: OpenFormula en ODF (`of:=`,
`[.A1:.B3]`, `;`) y la sintaxis de OOXML (sin `=`, nombres ingleses, `,`). Detalle en [12](12_FORMATOS.md).

## F-10 Recalcular

```mermaid
flowchart TD
    A["recalcular(libro)"] --> B["pendientes = celdas sucias + volátiles (AHORA, ALEATORIO...)"]
    B --> C{"¿quedan pendientes?"}
    C -- no --> Z([fin: lista de celdas que cambiaron, para repintar])
    C -- sí --> D["c = siguiente pendiente"]
    D --> E["evaluar(c)"]
    E --> F["c: Calculando (E-04)"]
    F --> G["ejecutar el código: por cada referencia leída"]
    G --> H{"estado de la celda leída"}
    H -- "Limpia" --> G2["usar su valor"]
    H -- "Sucia" --> G3["evaluar esa primero (recursivo, con pila propia si es muy honda)"]
    H -- "Calculando" --> CI["círculo: todas las del ciclo → Err:522 (Circular)"]
    G2 --> G
    G3 --> G
    G --> I{"¿función desconocida?"}
    I -- sí --> I1["conservar el valor del fichero; marca de desfasada"]
    I -- no --> J["valor = cima de la pila"]
    I1 --> K
    J --> K["c: Limpia; si el valor cambió, apuntarla para repintar"]
    CI --> K
    K --> C
```

Propuesta: la recursión de "evaluar esa primero" puede ser muy honda (una columna de 10.000 fórmulas que suman la de
encima). Para no agotar la pila del Amiga (16-32 KB), el orden se calcula con una lista de trabajo propia en lugar de
llamadas recursivas. Se decide al escribirlo (H3).

Las dependencias: cada fórmula apunta las celdas y rangos que lee. El índice inverso ("quién lee esta celda") se
guarda por celda para las referencias sueltas y en una lista aparte para los rangos (un rango `A:A` no apunta un
millón de celdas). Al marcar sucias se recorren los dos.

## F-11 Pintar la rejilla y repintar una zona

```mermaid
flowchart TD
    A{"¿quién pide?"}
    A -- "MUI (ventana nueva, tamaño, se destapa)" --> B["pinta_rejilla(x, y, ancho, alto): todo lo visible"]
    A -- "desplazamiento" --> B
    A -- "celdas cambiadas (F-07, F-10)" --> C["por cada celda: su rectángulo en pantalla, si es visible"]
    C --> C1["unir rectángulos cercanos; mui_canvas_update_area por cada uno"]
    C1 --> B2["pinta_rejilla del trozo"]
    B --> D["cabeceras de columnas y filas visibles (con inmovilizado)"]
    B2 --> E
    D --> E["por cada fila visible y cada columna visible"]
    E --> F["fondo y bordes del estilo"]
    F --> G["texto: valor formateado (core/numeros), en Latin-1 para pintar (A3), alineado, recortado o desbordando a la vecina vacía"]
    G --> H["marca de función desconocida (CU-C02)"]
    H --> E
    E --> I["líneas de la cuadrícula"]
    I --> J["selección y celda activa encima"]
    J --> Z(["fin: el doble búfer lo muestra de una vez"])
```

El texto formateado de cada celda visible se guarda en una caché pequeña (propuesta) para no volver a formatear al
desplazar una fila.

## F-12 Una tecla en Write

```mermaid
sequenceDiagram
    participant U as Usuario
    participant W as write.dash
    participant C as write/cursor
    participant D as write/documento
    participant DH as core/deshacer
    participant MQ as write/maqueta
    participant PG as write/paginas
    participant PI as write/pintor

    U->>W: tecla 'a' en el lienzo
    W->>C: cursor_tecla(código, calificadores D11)
    alt hay selección
        C->>D: borrar la selección (una orden)
    end
    C->>DH: orden "insertar texto" (se une a la anterior si es seguida)
    C->>D: parrafo_insertar(p, byte, "a")
    D->>D: mover tramos desde byte, tirar la caché de maqueta de p (E-07)
    C->>C: cursor = byte + largo UTF-8 (D5)
    W->>MQ: maquetar_parrafo(p)
    MQ-->>W: líneas nuevas de p (¿cambió el alto?)
    alt el alto de p no cambió
        W->>PI: repintar solo las líneas de p que cambiaron
    else cambió
        W->>PG: repaginar_desde(p) (F-13)
        PG-->>W: primera página distinta
        W->>PI: repintar desde esa página hasta el final de la vista
    end
    PI-->>U: se ve la letra (objetivo: menos de 50 ms, RNF-W02)
```

Lo mismo para borrar, pegar o aplicar formato: cambia uno o varios párrafos, se maquetan esos y se repagina desde
el primero.

## F-13 Repaginar

```mermaid
flowchart TD
    A["repaginar_desde(p)"] --> B["página y altura usada donde empieza p (guardadas de la última vez)"]
    B --> C["por cada bloque desde p"]
    C --> D{"¿caché de maqueta válida?"}
    D -- no --> D1["maquetar_parrafo (o tabla)"] --> E
    D -- sí --> E["colocar sus líneas en la página; si no caben, página nueva"]
    E --> F{"¿salto de página o de sección antes?"}
    F -- sí --> F1["página nueva (con el tamaño de su sección)"] --> E
    F -- no --> G{"¿el bloque empieza en la misma página y altura que antes?"}
    G -- "sí, y ya pasó del bloque cambiado" --> Z(["parar: de aquí en adelante todo sigue igual"])
    G -- no --> H["guardar su nueva posición"]
    H --> C
    C -- "no quedan" --> Z2(["fin: número de páginas"])
```

Parar en cuanto un bloque vuelve a caer donde estaba es lo que hace que escribir al principio de un documento largo
no repagine todo. Viudas, huérfanas y "conservar con el siguiente" vienen después (ARQUITECTURA § 6.2).

## F-14 Deshacer y rehacer

```mermaid
flowchart TD
    A["Usuario: Deshacer"] --> B{"¿pila de deshacer vacía?"}
    B -- sí --> Z0(["nada: el menú ya estaba desactivado"])
    B -- no --> C["o = sacar de deshacer"]
    C --> D["o.deshacer(doc): aplica lo contrario con lo que guardó"]
    D --> E["meter o en rehacer"]
    E --> F["selección y cursor: donde estaban al hacer o"]
    F --> G{"¿la pila llegó a la marca del último guardado?"}
    G -- sí --> G1["doc: sin cambios"]
    G -- no --> G2["doc: con cambios"]
    G1 --> H["recalcular (Calc) o repaginar desde lo tocado (Write); repintar"]
    G2 --> H
    H --> Z([fin])
    N["Usuario hace una orden nueva"] --> N1["meter en deshacer; vaciar rehacer"]
    N1 --> N2{"¿más de N pasos? (mínimo 100, RF-N08)"}
    N2 -- sí --> N3["tirar la más vieja"]
```

Cada orden (`core/deshacer`) guarda lo justo para volver: el valor viejo de una celda, el texto borrado y sus tramos,
los estilos de antes de un rango. Una orden compuesta (pegar, ordenar, reemplazar todo) agrupa varias.

## F-15 Copiar

```mermaid
sequenceDiagram
    participant U as Usuario
    participant P as Calc o Write
    participant PP as core/portapapeles
    participant CL as clipboard.device

    U->>P: Amiga+C con una selección
    P->>P: texto = selección como texto (Calc: valores formateados, tabulador entre celdas, salto entre filas)
    P->>P: bloque = selección con formato (formato propio de Lorraine, propuesta)
    P->>PP: portapapeles_poner(texto, bloque)
    PP->>PP: texto a Latin-1 (D5) para FTXT
    PP->>CL: IFF FORM FTXT (CHRS) + bloque con su identificador (D18)
    CL-->>U: listo, otros programas pueden pegar el texto
```

Cortar es copiar más una orden de borrar (una sola para deshacer). Que el bloque propio vaya en el mismo FORM o en
otra unidad del portapapeles se decide en D18.

## F-16 Pegar

```mermaid
flowchart TD
    A["Amiga+V"] --> B["portapapeles_leer()"]
    B --> C{"¿hay bloque de Lorraine?"}
    C -- sí --> D{"¿de qué tipo y dónde se pega?"}
    D -- "celdas en Calc" --> D1["copiar celdas con estilos y fórmulas (referencias relativas se mueven)"]
    D -- "celdas en Write" --> D2["tabla con valores formateados (desde H8; antes, texto)"]
    D -- "texto con formato en Write" --> D3["párrafos y tramos"]
    D -- "texto con formato en Calc" --> D4["un párrafo por fila, sin formato"]
    C -- no --> E{"¿hay FTXT?"}
    E -- no --> Z0([nada])
    E -- sí --> F["Latin-1 a UTF-8 (D5)"]
    F --> G{"programa"}
    G -- Calc --> G1["líneas → filas, tabuladores → columnas; F-08 a cada valor"]
    G -- Write --> G2["líneas → párrafos con el estilo del cursor"]
    D1 --> H
    D2 --> H
    D3 --> H
    D4 --> H
    G1 --> H
    G2 --> H["una orden compuesta para deshacer"]
    H --> I["Calc: F-10 y F-11. Write: F-13 desde el primer párrafo tocado"]
    I --> Z([fin])
```

En Calc se pega desde la celda activa. Si pisa celdas con datos, pregunta antes, como LibreOffice (propuesta: con
una casilla para no volver a preguntar).
