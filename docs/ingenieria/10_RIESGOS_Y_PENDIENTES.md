# 10. Riesgos y pendientes

Lo que puede fallar, lo que queda fuera, las preguntas de diseño abiertas y las decisiones que tiene que tomar el
usuario. Escrito el 2026-10-24, antes del código: los riesgos son **previstos**, no observados. Se revisa al cerrar
cada hito de [11](11_PLAN_DE_CONSTRUCCION.md).

## 1. Riesgos

Probabilidad e impacto: A (alto), M (medio), B (bajo).

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R-01 | **El lector XML en Dash va lento** (decisión A5). Todo fichero pasa por él; un `content.xml` de varios MB, carácter a carácter, puede tardar mucho en un 68k. | M | A | Medida PR-B01 en H1 contra expat compilado para 68k. Si va más de 3 veces más lento, se revisa A5 (expat de reserva). Antes, lo que haga falta en Dash (búferes, textos sin copiar) como tareas D. |
| R-02 | **Memoria con libros grandes.** Cada celda es un struct de Dash con su cabecera y su contador; decenas de miles de celdas pueden no caber en un Amiga normal. | M | A | Medida PR-B03 en H2 (objetivo < 40 bytes por celda). D17 (reducir la cabecera). Si no basta: celdas de número sin struct propio, en listas de `Double` por fila (D2). |
| R-03 | **Dos ramas de Dash tocando el compilador a la vez:** `dashweb` (Tachyon) y `lorraine`. Las dos cambian `codegen.py`, `amiga_builtins.py` y el runtime; al fusionar en `main` puede haber conflictos o cambios que se pisan sin que falle nada a la vista. | A | M | Fusionar en `main` a menudo y en tandas pequeñas. Cada tarea D con su test en la batería de Dash (si una fusión rompe algo, salta ahí). Avisar a la sesión de Dash de Tachyon antes de tocar piezas comunes (MUI, lienzo, memoria). Compartir emulador y puertos de pruebas con cuidado, como ya hace Tachyon. |
| R-04 | **Dependencia de Dash, que crece a la vez.** Hitos bloqueados esperando tareas D (D1 bloquea H2; D5 y D6, H1). | A | M | Pedir las D de cada hito antes de empezarlo. Mientras, trabajar en lo que no depende de ellas (por ejemplo, los filtros sobre texto antes de los números). |
| R-05 | **Sin Excel ni Word** para comprobar los `.xlsx` y `.docx` que guarda Lorraine (decisión del usuario, 2026-10-25: no se usan). Un fichero puede abrir en LibreOffice y dar "reparar" en Excel. | M | A | Validador del Open XML SDK (OOXML-Validator, con .NET en `~/.cache`) y tres lectores distintos: LibreOffice, OnlyOffice y openpyxl/python-docx ([08](08_PLAN_DE_PRUEBAS.md) § 4.4). Copiar la estructura de los ficheros reales del corpus externo y seguir [MS-OI29500]. Lo que algún usuario encuentre en Excel, al corpus. |
| R-06 | **Las páginas de Write no salen exactamente como en Word o LibreOffice.** | M | M | Las fuentes de A13 miden lo mismo que Arial, Times New Roman, Courier New, Calibri y Cambria: con ellas las líneas cortan casi igual. Siguen las diferencias por otras fuentes (por ejemplo Aptos, la de Word desde 2023, que no tiene gemela libre), por el interlineado y por la partición de palabras. Se conserva el contenido y el formato, no la paginación (arquitectura § 6.2). |
| R-07 | **`Double` por software si alguien compila sin FPU.** Cada operación de coma flotante pasa a ser una llamada, muchas veces más lenta. Y mezclar partes con y sin FPU rompe los números (lo vivió Tachyon). | M | M | Se publica y se mide solo con `--fpu` (requisito: 68020 + FPU). La versión sin FPU solo tiene que compilar. Todo el C de `third_party/` con `-m68881`. |
| R-08 | **Fuentes.** Hasta el H8 la pantalla de Write pinta con fuentes del Amiga parecidas, aunque la maqueta ya use las medidas de A13. Pintar TrueType en un 68030 puede ser lento. | M | M | Caché de caracteres ya pintados por fuente y tamaño. Las fuentes de A13 tienen licencia OFL 1.1, que permite llevarlas en el paquete junto a programas MIT, con su licencia al lado. D23 y D24. |
| R-09 | **Formatos enormes.** OOXML (ISO/IEC 29500) y ODF tienen miles de páginas de especificación y cada programa escribe sus variantes. Siempre habrá ficheros que Lorraine lea mal. | A | M | Leer lo común primero, apoyado en el corpus real. RF-C11 y el aviso de pérdidas (A9) cubren lo que falta. Un fichero que falla se añade al corpus. |
| R-10 | ~~El nombre "Lorraine" sin comprobar en Aminet.~~ Comprobado el 2026-10-25: en Aminet solo hay dos módulos de música con ese nombre; en GitHub, nada de Amiga ni de ofimática. | — | — | Cerrado. |
| R-11 | **El código de Ignition (GPL v3).** Leerlo para entender cómo resuelve algo puede acabar en copia sin querer. | B | A | No tener su código abierto mientras se escribe el equivalente. Escribir primero el diseño en palabras. Revisión en cada hito (RNF-06). |
| R-12 | **El teclado del Amiga** no tiene Inicio, Fin, RePág ni AvPág, y la interfaz propone atajos con Alt ([06](06_INTERFAZ_DE_USUARIO.md) § 2.4). Pueden chocar con las teclas muertas del mapa de teclado (Alt + letra da acentos). | M | B | Solo Alt + flechas, que no son teclas muertas. Comprobar con los mapas de teclado español y alemán. |
| R-13 | **Pruebas de interfaz frágiles.** Los clics por `input.device` dependen de la posición de cada objeto y de la fuente de la pantalla. | M | M | Probar la lógica sin ventana todo lo posible (órdenes de edición como funciones con su test). Pocas pruebas de interfaz, de flujos enteros. Modo `TEST` del programa ([08](08_PLAN_DE_PRUEBAS.md) § 6). |
| R-14 | **Recálculo lento con muchas dependencias** (un rango `A:A` en mil fórmulas, `INDIRECTO`, `DESREF`). | M | M | Rangos guardados como rango en el grafo, no celda a celda. `INDIRECT` y `OFFSET` como volátiles. Medida PR-C02. |
| R-15 | **Bombas de ZIP y ficheros malos** que agoten la memoria. | B | A | Tope al descomprimir según el tamaño declarado y la memoria libre; corpus de ficheros malos ([08](08_PLAN_DE_PRUEBAS.md) § 5). |
| R-16 | **Hojas con algo muy abajo.** Una celda en la fila 1.000.000 haría una lista de un millón de huecos (4 MB) con el modelo disperso por filas. | M | A | Decidir antes del H2: filas en una lista compacta ordenada por número (búsqueda binaria, D10) o un diccionario con clave `Int` (D9). Libro de prueba en el corpus de ficheros malos. |
| R-17 | **Recursión que agota la pila.** Recalcular una cadena de 10.000 fórmulas o leer una fórmula muy anidada con funciones recursivas desborda la pila de 16-32 KB. | M | A | Recálculo con bucle y lista de pendientes, nunca recursivo ([ARQUITECTURA](../ARQUITECTURA.md) § 5.2). El parser de fórmulas pone un tope de anidamiento (Excel admite 64 niveles). Test con una cadena larga. |
| R-19 | **Velocidad en un 68030 real** (máquina mínima desde el 2026-10-25). Lector XML en Dash, recálculo, pintar la rejilla y las TrueType, todo en una CPU varias veces más lenta que un 68040 con JIT. | A | A | Los objetivos de rendimiento se miden en "a1200-030" desde el H1 (PR-B01) y el H2. Repintar solo lo que cambia. Lo lento de Dash, como tareas D. Si un objetivo no se alcanza, se habla con el usuario antes de bajarlo. |
| R-18 | **Cifrado o formato antiguo.** Un `.xlsx` cifrado y un `.xls` empiezan igual (fichero compuesto OLE2). Para dar el aviso correcto hay que leer su directorio ([12](12_FORMATOS.md) § 7). | A | B | Un lector mínimo del directorio OLE2 en `core/paquete`. Si no se hace a tiempo, un aviso común: "formato antiguo o protegido con contraseña". |

## 2. Funcionalidad que queda fuera de la 1.0

La de [ARQUITECTURA](../ARQUITECTURA.md) § 10 y [11](11_PLAN_DE_CONSTRUCCION.md) § 4: macros, tablas dinámicas,
gráficos, formato condicional, validación de datos, control de cambios, comentarios, notas al pie, ecuaciones,
objetos incrustados, documentos cifrados, `.xls`, `.doc`, RTF. Al abrir un documento que los tiene, se apuntan como
pérdidas (A9).

## 3. Preguntas de diseño abiertas

Las resuelve el desarrollo en el hito que se indica, sin necesidad del usuario salvo que cambien una decisión A.

| Pregunta | Hito |
|---|---|
| Editar la celda dentro del lienzo, con el mismo editor de una línea que Write, o solo en el campo de fórmula | H3 |
| Cómo se guardan las celdas de número para ahorrar memoria (ver R-02) | H2 |
| Formato del portapapeles propio entre Calc y Write (identificador IFF) | H5 |
| Dónde se guardan las preferencias (`ENVARC:Lorraine/`, un fichero por programa) | H5 |
| Si cerrar la última ventana cierra el programa | H5 |
| Nombres de funciones en español: en el programa o en el catálogo ([09](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md) § 5) | H3 |

## 4. Deuda técnica

Ninguna todavía: no hay código. Se empieza a llevar en H1.

## 5. Decisiones del usuario

Tomadas el 2026-10-25:

| Decisión | Resultado | Dónde se aplica |
|---|---|---|
| ¿Debe ir bien en un A1200 con 68030 real? | **Sí.** Es la máquina de los objetivos de rendimiento. | Arquitectura § 1, RNF, [08](08_PLAN_DE_PRUEBAS.md) § 2 y § 8, R-19 |
| ¿Con qué letra se maqueta el PDF? | Recomendación aceptada: las fuentes de A13 (Liberation, Carlito, Caladea), las mismas en pantalla y en PDF, incrustadas. | Arquitectura A13, H6 y H9 |
| ¿Idioma de la interfaz? | Inglés de base, con catálogos de varios idiomas; el español, el primero. | A11, [09](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md) § 5 |
| ¿Repositorio en GitHub? | Nombre comprobado y repositorio público `FreeMEM/lorraine` creado. | [09](09_ENTORNO_CONSTRUCCION_Y_ENTREGA.md) § 7 |
| ¿Quién prueba en Excel y Word? | Nadie: se comprueba con LibreOffice, OnlyOffice y librerías de Python, más el validador. | R-05, [08](08_PLAN_DE_PRUEBAS.md) § 4.4 |

Pendiente: si el 68030 de la máquina mínima puede no llevar FPU. Hoy se supone que la lleva (R-07).
