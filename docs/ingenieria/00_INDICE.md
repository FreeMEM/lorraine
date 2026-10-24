# Documentación de ingeniería de Lorraine

Especificación de Lorraine, la suite ofimática para AmigaOS 3.x con interfaz MUI, escrita en Dash: Lorraine Calc
(hoja de cálculo) y Lorraine Write (procesador de textos). Está pensada para que un equipo pueda construirla desde
cero con ella.

- **Versión del documento:** 0.1, 2026-10-25.
- **Estado:** diseño previo. Todavía no hay código. Todo requisito está pendiente y todo nombre de módulo o función es
  una propuesta. Cuando haya código, los documentos se ponen al día contra él, como en Tachyon.

## Documentos

| Nº | Documento | Qué contiene | Para quién |
|---|---|---|---|
| — | [Arquitectura](../ARQUITECTURA.md) | Piezas, repositorio, modelos, abrir y guardar, decisiones (A1-A12) con su porqué, memoria, lo que queda fuera | Todo el equipo |
| 01 | [Requisitos](01_REQUISITOS.md) | Alcance, requisitos funcionales comunes (RF-N), de Calc (RF-C) y de Write (RF-W), funciones de Calc, no funcionales (RNF) | Producto, todo el equipo |
| 02 | [Casos de uso](02_CASOS_DE_USO.md) | Actores y casos de uso (CU) con flujo principal, alternativas y errores | Producto, QA |
| 03 | [Flujos](03_FLUJOS.md) | Diagramas de flujo y de secuencia (F): abrir, guardar, fórmulas, recálculo, pintado, tecleo, deshacer, portapapeles | Desarrollo |
| 04 | [Estados](04_ESTADOS.md) | Diagramas de estado (E): documento, edición de celda, recálculo, carga, cursor, caché de maqueta | Desarrollo, QA |
| 05 | [Modelo de datos](05_MODELO_DE_DATOS.md) | Structs del libro y del documento, dueños y vida, código de fórmulas, errores, memoria por celda y párrafo | Desarrollo |
| 06 | [Interfaz de usuario](06_INTERFAZ_DE_USUARIO.md) | Ventanas, menús y atajos, teclado, mensajes, ventanas secundarias | Diseño, desarrollo, QA |
| 07 | [Módulos e interfaces](07_MODULOS_E_INTERFACES.md) | Cada módulo de `core/`, `calc/` y `write/`: responsabilidad, dependencias, funciones públicas propuestas | Desarrollo |
| 08 | [Plan de pruebas](08_PLAN_DE_PRUEBAS.md) | Estrategia, corpus, ida y vuelta con LibreOffice, validadores, aceptación (PA), rendimiento (PR), criterios de publicación | QA |
| 09 | [Entorno, construcción y entrega](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md) | Herramientas, Dash, emulador, librerías de C, construcción, paquete, publicación | Desarrollo, entrega |
| 10 | [Riesgos y pendientes](10_RIESGOS_Y_PENDIENTES.md) | Riesgos (R), decisiones pendientes del usuario | Dirección, todo el equipo |
| 11 | [Plan de construcción](11_PLAN_DE_CONSTRUCCION.md) | Hitos H0-H11 en orden de dependencia, con entregables, aceptación y tareas de Dash; versiones | Dirección, desarrollo |
| 12 | [Formatos de fichero](12_FORMATOS.md) | ODF y OOXML: paquetes, partes, lo que se lee y escribe, correspondencia con el modelo, pérdidas, cifrado, validadores | Desarrollo |
| 13 | [Lo que hay que añadir a Dash](13_DASH.md) | Tareas D1-D34 con su porqué, prioridad e hito; cómo se piden | Desarrollo, Dash |

El plan de trabajo y la bitácora están en [`docs/LORRAINE_LOOP.md`](../LORRAINE_LOOP.md).

## Por dónde empezar

- **Para entender qué es:** arquitectura, 01 y 02.
- **Para programar:** arquitectura, 05, 07, 12 y 03.
- **Para trabajar en Dash:** 13.
- **Para montar el entorno:** 09.
- **Para probar:** 08.
- **Para planificar:** 11 y 10.

## Convenciones

- **IDs:** A (decisión de arquitectura), RF-N / RF-C / RF-W (requisito funcional común, de Calc, de Write), RNF
  (no funcional), CU (caso de uso), F (flujo), E (estado), PA (prueba de aceptación), PR (prueba de rendimiento),
  R (riesgo), H (hito), D (tarea de Dash; en el repositorio de Dash, "lorraine D<n>").
- **Nombres:** módulos y funciones en español, con el prefijo de su módulo (`libro_celda`, `xml_siguiente`). Los
  builtins de Dash, en inglés, como el resto de Dash.
- **Medidas:** twips en la maqueta (1/1440 de pulgada); bytes y milisegundos en los requisitos.
- **Fórmulas:** con nombres ingleses en la documentación (`SUM`); el usuario las ve en su idioma.

## Glosario

| Término | Significado |
|---|---|
| AmigaOS 3.x | El sistema operativo del Amiga clásico (3.1, 3.2, 3.5, 3.9). |
| Dash | Lenguaje que compila a C para el Amiga (repositorio `FreeMEM/dash`). Lorraine está escrita en él. |
| MUI | Magic User Interface: la librería de interfaces gráficas del Amiga (versiones 3.8 y 5). |
| `.dashui` | Fichero con ventanas MUI hecho con el editor visual de Dash; el compilador lo importa como módulo. |
| ODF | OpenDocument Format, el de LibreOffice (`.ods`, `.odt`). Norma OASIS e ISO/IEC 26300. |
| Flat ODF | ODF en un solo XML, sin ZIP (`.fods`, `.fodt`). |
| OOXML | Office Open XML, el de Microsoft Office desde 2007 (`.xlsx`, `.docx`). Norma ECMA-376 e ISO/IEC 29500. |
| Paquete | El ZIP de un documento ODF u OOXML, con sus partes (ficheros XML, imágenes). |
| OpenFormula | La forma de escribir fórmulas en ODF (`of:=SUM([.A1:.B2])`). |
| Twip | 1/1440 de pulgada (1/20 de punto). Unidad de maqueta de Lorraine y de OOXML. |
| Libro, hoja, celda | El documento de Calc, cada una de sus pestañas y cada casilla. |
| Tramo | Un trozo de un párrafo con el mismo formato de carácter. |
| Pérdida | Algo del fichero abierto que Lorraine no entiende y no guardará (decisión A9). |
| Corpus | Los documentos de prueba de `tests/ficheros/`. |
| Ida y vuelta | Abrir con Lorraine, guardar, abrir con LibreOffice y comparar. |
| FS-UAE | Emulador de Amiga con el que se ejecutan los tests. |
| `--memcheck` | Opción de Dash que comprueba al salir que no queda memoria sin liberar. |
| Ignition | Hoja de cálculo libre para Amiga (GPL v3). Se puede leer para aprender; su código no se copia. |
