# 04. Diagramas de estado

Los objetos de Lorraine que cambian de estado, y qué los hace cambiar. Diseño de partida, antes del código: los
nombres de campos son propuestas. Los flujos que los mueven están en [03](03_FLUJOS.md); sus datos, en
[05](05_MODELO_DE_DATOS.md).

| ID | Objeto | Programa | Dónde vivirá el estado (propuesta) |
|---|---|---|---|
| E-01 | Un documento | Los dos | `Libro` / `Documento`: `ruta`, `formato`, `cambios` y `cambios_al_guardar`, pila de deshacer con su marca de guardado |
| E-02 | La edición de una celda | Calc | La ventana de Calc: `modo` (navegar, escribir, señalar) |
| E-03 | La selección de Calc | Calc | La ventana: `activa`, `ancla`, `rango` |
| E-04 | El cálculo de una celda | Calc | `Celda`: `calculo` (limpia, sucia, calculando, circular) |
| E-05 | La carga de un fichero | Los dos | El filtro mientras lee |
| E-06 | El cursor y la selección de Write | Write | `write/cursor`: posición, ancla, arrastre |
| E-07 | La caché de maqueta de un párrafo | Write | `Parrafo`: `lineas` (nil = sin maquetar), `alto`, `pagina`, `y` |

## E-01 Un documento

```mermaid
stateDiagram-v2
    [*] --> Nuevo: Proyecto › Nuevo, o arranque sin ficheros
    [*] --> Cargando: Abrir (E-05)
    Cargando --> Limpio: bien
    Cargando --> [*]: error (CU-N06)
    Nuevo --> Modificado: primer cambio
    Nuevo --> [*]: Cerrar (sin preguntar)
    Limpio --> Modificado: cualquier orden de edición
    Modificado --> Limpio: deshacer hasta la marca de guardado
    Limpio --> Modificado: rehacer o deshacer más allá de la marca
    Modificado --> Guardando: Guardar
    Nuevo --> Guardando: Guardar (pide nombre)
    Limpio --> Guardando: Guardar como
    Guardando --> Limpio: bien (marca de guardado aquí, pérdidas vacías)
    Guardando --> Error: disco, memoria, cancelado
    Error --> Modificado: el aviso se cierra (el original sigue intacto)
    Error --> Nuevo: el aviso se cierra (si nunca se había guardado)
    Limpio --> [*]: Cerrar
    Modificado --> Preguntando: Cerrar o Salir
    Preguntando --> Guardando: Guardar
    Preguntando --> [*]: No guardar
    Preguntando --> Modificado: Cancelar

    state Guardando {
        state "¿Pérdidas?" as Perdidas
        [*] --> Perdidas
        Perdidas --> Avisando: mismo formato y hay pérdidas (CU-N03)
        Perdidas --> Escribiendo: no
        Avisando --> Escribiendo: Guardar igualmente
        Escribiendo --> Cambiando: temporal escrito
        Cambiando --> [*]: original sustituido
    }
```

- **Limpio / Modificado** no es un booleano suelto: es comparar la posición de la pila de deshacer con la marca del
  último guardado. Así deshacer hasta lo guardado deja el documento "sin cambios" (F-14).
- Un "Cancelar" en Avisando sale de Guardando sin error, al estado de antes.
- El `*` del título de la ventana sigue a Modificado (F-02, `ventana_al_dia`).

## E-02 La edición de una celda (Calc)

```mermaid
stateDiagram-v2
    [*] --> Navegando
    Navegando --> Escribiendo: tecla imprimible (borra el contenido)
    Navegando --> Escribiendo: F2, doble clic o clic en el campo de fórmula (conserva el contenido)
    Navegando --> Navegando: flechas, Tab, Return, clic (mueve la celda activa, E-03)
    Escribiendo --> Señalando: tras '=', '(', punto y coma, un operador, y luego flecha o clic en la rejilla
    Señalando --> Señalando: flechas o arrastre cambian la referencia que se está insertando
    Señalando --> Escribiendo: tecla imprimible (la referencia queda escrita)
    Escribiendo --> Navegando: Return, Tab, flecha (acepta, F-07)
    Señalando --> Navegando: Return o Tab (acepta)
    Escribiendo --> Navegando: Esc (descarta)
    Señalando --> Navegando: Esc (descarta)
    Escribiendo --> Escribiendo: fórmula con error (aviso, no sale)
```

- En Escribiendo, las flechas mueven el cursor dentro del texto si se entró con F2 o en el campo de fórmula; si se
  entró tecleando, aceptan y mueven la celda activa, como en LibreOffice.
- En Señalando, la referencia se escribe en el texto con el formato del idioma (`A1`, `$A$1` con F4, `Hoja2.A1` en
  otra hoja). El rango señalado se dibuja con un marco de color.
- Mientras se está en Escribiendo o Señalando, los menús que cambian el libro (insertar filas, ordenar) están
  desactivados.

## E-03 La selección de Calc

```mermaid
stateDiagram-v2
    [*] --> Celda: celda activa A1
    Celda --> Celda: flecha, clic, Return, Tab
    Celda --> Rango: Shift+flecha, Shift+clic, arrastre (D11, D12)
    Rango --> Rango: Shift+flecha, arrastre (ancla fija, el otro extremo se mueve)
    Rango --> Celda: flecha o clic sin Shift
    Celda --> Filas: clic en cabecera de fila
    Celda --> Columnas: clic en cabecera de columna
    Filas --> Filas: Shift+clic o arrastre por las cabeceras
    Columnas --> Columnas: Shift+clic o arrastre por las cabeceras
    Filas --> Celda: clic en una celda
    Columnas --> Celda: clic en una celda
    Celda --> Todo: Amiga+A o clic en la esquina
    Rango --> Todo: Amiga+A
    Todo --> Celda: clic o flecha
    Celda --> Arrastrando: arrastre empieza sobre una celda
    Arrastrando --> Rango: botón suelto
```

- La selección guarda siempre una celda activa (dentro del rango), el ancla y el rango. Return y Tab dentro de un
  rango recorren sus celdas sin perderlo.
- Selecciones múltiples (Ctrl+clic) quedan fuera de la primera versión (propuesta).
- La barra de estado muestra suma, promedio y cuenta de la selección (RF-C23).

## E-04 El cálculo de una celda (Calc)

Solo las celdas con fórmula tienen este estado. El resto está siempre limpio.

```mermaid
stateDiagram-v2
    [*] --> Sucia: fórmula nueva (escrita, pegada)
    [*] --> Limpia: leída de un fichero con su valor (A8)
    Limpia --> Sucia: cambia una celda que lee, o es volátil y toca recalcular
    Sucia --> Calculando: recalcular la evalúa (F-10)
    Calculando --> Limpia: valor obtenido (o error normal: #¡DIV/0!, #N/D...)
    Calculando --> Circular: lee una celda que también está Calculando
    Circular --> Sucia: cambia algo del ciclo
    Limpia --> Desconocida: tiene una función que Lorraine no sabe calcular
    Desconocida --> Desconocida: cambia algo que lee (conserva el valor, marca de desfasada)
    Desconocida --> Sucia: el usuario la edita con funciones conocidas
```

- **Circular** muestra `Err:522`. Todas las celdas del ciclo pasan a Circular, no solo la que lo descubre.
- **Desconocida** es una Limpia con una marca: su valor es el del fichero y no se recalcula (CU-C02). Se propone un
  estado aparte para que la rejilla pinte la marca sin mirar la fórmula.
- Al cerrar Calculando no queda ninguna celda en ese estado; si quedara una, es un fallo del motor (se comprueba en
  los tests).

## E-05 La carga de un fichero

```mermaid
stateDiagram-v2
    [*] --> Detectando: paquete_detectar (F-04)
    Detectando --> Fallo: dañado, cifrado, antiguo, desconocido, del otro programa
    Detectando --> LeyendoManifiesto: ZIP de ODF u OOXML
    Detectando --> LeyendoPlano: FODS, FODT, CSV, TXT
    LeyendoManifiesto --> LeyendoEstilos: manifest.xml o [Content_Types].xml + .rels
    LeyendoEstilos --> LeyendoContenido: styles.xml / xl/styles.xml / word/styles.xml (+ numbering)
    LeyendoContenido --> LeyendoContenido: siguiente entrada (cada hoja de xlsx, sharedStrings...)
    LeyendoContenido --> Terminando: no quedan entradas
    LeyendoPlano --> Terminando: fin del fichero
    Terminando --> Listo: Calc compila fórmulas, Write prepara la primera página
    LeyendoManifiesto --> Fallo: falta una parte obligatoria
    LeyendoEstilos --> Fallo: XML roto, sin memoria
    LeyendoContenido --> Fallo: XML roto, sin memoria, CRC mal
    LeyendoPlano --> Fallo: XML roto, sin memoria
    Fallo --> [*]: se libera lo leído, mensaje (CU-N06)
    Listo --> [*]: documento en Limpio (E-01)
```

- Dentro de cada estado de lectura, el filtro va entrada a entrada: descomprimir, leer a eventos, soltar el búfer
  (F-05). Solo una entrada descomprimida a la vez.
- En `.xlsx` el orden importa: `sharedStrings.xml` y `styles.xml` antes que las hojas, porque las celdas los citan
  por número. En `.ods`, `styles.xml` antes que `content.xml`.
- Propuesta: con ficheros grandes, la barra de estado muestra el avance por entradas y bytes. Si cancelar la carga
  a mitad hace falta, se añade un estado Cancelando que va a Fallo sin mensaje.

## E-06 El cursor y la selección de Write

```mermaid
stateDiagram-v2
    [*] --> Cursor: inicio del documento
    Cursor --> Cursor: escribir, flechas, Inicio, Fin, Re Pág, Av Pág, clic
    Cursor --> Seleccion: Shift+flecha, Shift+clic (D11)
    Cursor --> Arrastrando: botón pulsado sobre el texto (D12)
    Arrastrando --> Arrastrando: mover (el extremo sigue al puntero, la vista se desplaza al salir por arriba o abajo)
    Arrastrando --> Seleccion: botón suelto lejos del ancla
    Arrastrando --> Cursor: botón suelto en el ancla
    Cursor --> Seleccion: doble clic (palabra), triple clic (párrafo), Amiga+A (todo)
    Seleccion --> Seleccion: Shift+flecha, Shift+clic (ancla fija)
    Seleccion --> Cursor: flecha o clic sin Shift (se pone al extremo)
    Seleccion --> Cursor: escribir o borrar (la selección se sustituye, F-12)
    Seleccion --> Seleccion: aplicar formato (la selección se queda)
```

- La posición es (párrafo, byte), siempre al inicio de un carácter UTF-8 (D5). Dentro de una tabla, además la celda.
- Al subir y bajar con las flechas se recuerda la x deseada, para no ir derivando hacia la izquierda en líneas
  cortas.
- El cursor parpadea con un temporizador (F-02). Al teclear se reinicia el parpadeo y se ve fijo.

## E-07 La caché de maqueta de un párrafo (Write)

```mermaid
stateDiagram-v2
    [*] --> SinMaquetar: párrafo leído o creado
    SinMaquetar --> Maquetado: maquetar_parrafo (líneas con su ancho y alto)
    Maquetado --> Colocado: repaginar lo pone en una página y altura
    Colocado --> SinMaquetar: cambia su texto, sus tramos o su estilo (F-12)
    Colocado --> SinMaquetar: cambia el estilo del que hereda, o el ancho de su página o de su celda
    Colocado --> Maquetado: se repagina desde antes de él (sus líneas siguen valiendo, la posición no)
    Colocado --> Colocado: repaginar lo vuelve a poner donde estaba (aquí para F-13)
    Colocado --> Liberado: falta memoria y su página está lejos de la vista (propuesta)
    Liberado --> Maquetado: hace falta verlo o repaginar a través de él
```

- **Liberado** guarda solo su alto total y su posición. Así repaginar no tiene que maquetarlo de nuevo si no cambió.
  Es una propuesta para RNF-W03; se decide en H6 con las medidas de memoria.
- Cambiar el zoom no invalida la caché, porque la maqueta está en twips (A10): el zoom solo afecta al pintor.
  Cambiar la fuente sí, porque cambian los anchos.
