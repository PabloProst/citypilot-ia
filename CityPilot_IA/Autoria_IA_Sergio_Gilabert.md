# Memoria individual de utilización de IA — CityPilot IA


## 1. Autoría y aportación individual

- Estudiante: Sergio Gilabert Solaz
- Repositorio GitHub: https://github.com/PabloProst/citypilot-ia
- Mis dos PR, con revisión cruzada: PR 1: (https://github.com/PabloProst/citypilot-ia/pull/4) y [PR 2: (https://github.comPabloProst/citypilot-ia/pull/8)
- Archivos o funciones que implementé personalmente:
  - "web/app/db.py": "guardar_solicitud", "obtener_estadisticas" y "obtener_ultimas_solicitudes" (la PR de "db.py" ya fue aceptada).
  - "web/templates/analitica.html": métricas, gráfica y tablas del panel de analítica (segunda PR).
  - Adaptación de los nombres de variables de la plantilla a la ruta "/analitica" de "main.py".

## 2. Herramientas y fuentes usadas

| Herramienta o fuente | Modelo/versión, si se conoce | Finalidad | ¿Se incorporó código o texto? |
|---|---|---|---|
| Claude (Anthropic), chat web/app | Sonnet 5.5 | Entender el enunciado de "db.py", aprender funciones y sintaxis de SQL/SQLAlchemy que aún no conozco, revisar mi código y generar el HTML/Jinja de "analitica.html" | Sí: en "db.py" (adaptado y revisado por mí) y en "analitica.html" (generado con IA y adaptado) |
| Enunciado de la práctica y "CREATE TABLE" de "solicitudes" | Proporcionados por el profesorado | Estructura de la tabla y requisitos | Sí, como base del trabajo |
| Git / GitHub | — | Control de versiones y pull requests | No aplica |

- No he usado otras herramientas de IA generativa distintas de Claude.

**Contexto importante sobre mi nivel:**

- **HTML:** nunca he estudiado HTML ni plantillas Jinja2, y no sabía programar "analitica.html". Por eso usé IA para generar la plantilla completa y después le pedí que me explicara cada parte.
- **SQL:** todavía estoy cursando la asignatura de Bases de Datos y estoy aprendiendo SQL. Por eso, en las consultas de "db.py", pregunté a la IA por funciones y construcciones de SQL que no conocía ("RETURNING", "CAST(... AS jsonb)", "COUNT(*) FILTER", "GROUP BY", parámetros con ":nombre").

## 3. Registro cronológico de uso RELEVANTE de IA y recursos externos

### Interacción 1 — comprensión del enunciado de "db.py"

- **Qué intentaba resolver:** no entendía qué pedía la tarea de implementar las tres funciones de "db.py" con SQLAlchemy.
- **Herramienta/fuente y prompt o instrucción:** Claude. Pegué la guía de implementación y pedí: "explícame esta tarea de manera básica paso por paso".
- **Qué propuso o respondió:** una explicación sencilla de la infraestructura ("engine", "text", "pool_pre_ping", "ping_db") y de los pasos de cada función.
- **Qué hice yo con ello:** lo usé para entender el objetivo de cada función antes de escribir código.
- **Resultado y verificación:** entendí la estructura general; la verificación posterior se hizo al implementar y probar las funciones.


### Interacción 2 — esqueleto con otro tema

- **Qué intentaba resolver:** ver la estructura del código sin que me dieran la solución directa.
- **Herramienta/fuente y prompt o instrucción:** Claude. "Dame un esqueleto mínimo de códigos de lo que hay que hacer, pero de otro tema".
- **Qué propuso o respondió:** un ejemplo con una tabla de libros ("guardar_libro", estadísticas, últimos libros) con la misma estructura que la práctica.
- **Qué hice yo con ello:** lo estudié como modelo y pedí que lo aplicara a mi práctica.
- **Resultado y verificación:** me sirvió para ver el patrón "engine.begin()" / "engine.connect()", "text()" con parámetros y "RETURNING id".


### Interacción 3 — dudas de SQL y sintaxis (aprendizaje)

- **Qué intentaba resolver:** entender consultas SQL y construcciones que aún no he visto en la asignatura de Bases de Datos.
- **Herramienta/fuente y prompt o instrucción:** Claude. Fui preguntando por líneas concretas, por ejemplo: "VALUES (:titulo, :genero, CAST(:etiquetas AS jsonb))", la lista completa de valores del INSERT, «¿para qué sirven los dos puntos?», «¿qué hace scalar_one()?», «¿por qué hay paréntesis y corchetes?», «¿qué es raise NotImplementedError?» y el docstring con TODO.
- **Qué propuso o respondió:** explicaciones de:
  - parámetros con nombre (":ciudad") y protección frente a inyección SQL;
  - "CAST(... AS jsonb)";
  - "RETURNING id" + ".scalar_one()";
  - "COUNT(*) FILTER (WHERE ...)" y "GROUP BY";
  - diferencia entre "registro["x"]" y "registro.get("x")".
- **Qué hice yo con ello:** usé las explicaciones para comprender el código que iba a entregar y poder explicarlo; los conceptos de SQL los estoy consolidando en la asignatura.
- **Resultado y verificación:** comprobé que entendía cada parte antes de integrarla. 


### Interacción 4 — revisión de mi "db.py"

- **Qué intentaba resolver:** saber si mi código cumplía el enunciado.
- **Herramienta/fuente y prompt o instrucción:** Claude. Pegué mi "db.py" y pregunté si fallaba algo, sabiendo las instrucciones de la práctica.
- **Qué propuso o respondió:** detectó un fallo real: el valor por defecto de "lugares" era "{}" (diccionario) en vez de "[]" (lista, que es el "DEFAULT" de la tabla). También sugirió:
  - limpiar posibles claves secretas con "pop";
  - comprobar si "engine" es "None";
  - alinear el "return" de "obtener_estadisticas".
- **Qué hice yo con ello:** saqué el "return" de "obtener_estadisticas" fuera del "with". También, corregí"lugares" y añadi el resto de sugerencias, menos la pop, que no veia ninguna variable sensible o al menos no lo he interpretado así.

### Interacción 5 — creación de "analitica.html" (HTML generado con IA)

- **Qué intentaba resolver:** completar la plantilla "analitica.html" (métricas, gráfica y tablas). **No he dado HTML ni plantillas Jinja2 y no sabía hacerlo**, así que dependí de la IA para este archivo.
- **Herramienta/fuente y prompt o instrucción:** Claude. Pegué la plantilla de partida con sus "TODO" y pedí el código para completarla.
- **Qué propuso o respondió:** una plantilla completa con:
  - las tres métricas con variables Jinja;
  - la imagen "/analitica/grafico.png";
  - la tabla del top 5;
  - la tabla de las 8 últimas peticiones, sin datos sensibles.
  La primera versión usaba variables supuestas ("stats", "ultimas") y la IA supuso erróneamente que el framework era FastAPI.
- **Qué hice yo con ello:**
  - Le pasé el código real de las rutas de "main.py" (Flask).
  - Pedí que adaptara el HTML a las variables reales ("totales", "top_ciudades", "ultimas").
  - Pregunté qué había pasado con el bloque original ("<div class="todo">" y los "—" de las métricas) para entender qué se había cambiado: solo se reformateó, y los marcadores provisionales se sustituyeron por datos reales.


## 4. Evolución del prompt de itinerarios (si utilizaste el LLM)

No he trabajado en el prompt de itinerarios ni he utilizado el LLM para generarlos. Mi parte se ha centrado en "db.py" consultas a PostgreSQL y en "analitica.html".

## 5. Código o materiales externos incorporados

| Archivo/líneas aproximadas | Origen (IA, documentación, GitHub, compañero...) | ¿Copiado o adaptado? | ¿Qué cambio/validación hice? |
|---|---|---|---|
| "web/app/db.py" / "guardar_solicitud", "obtener_estadisticas", "obtener_ultimas_solicitudes" | Claude (esqueleto de ejemplo y propuesta de código) | Adaptado | Usé consultas parametrizadas con "text()" y parámetros con nombre (":ciudad", ":pais", ...) en lugar de concatenar strings; "CAST(:meteorologia AS jsonb)" y "CAST(:lugares AS jsonb)" para los campos JSON; "RETURNING id" con ".scalar_one()" para obtener el ID; y "COUNT(*) FILTER" y "GROUP BY" para las estadísticas. Comprobé que cada ":parámetro" del SQL tiene su clave en el diccionario y que las columnas y los valores del "INSERT" van en el mismo orden. |
| "web/templates/analitica.html" (completo) | Claude | Generado con IA y adaptado | Cambié los nombres de variables a los de mi ruta Flask ("totales", "top_ciudades", "ultimas"). |

## 6. Balance personal

- **Dos decisiones técnicas que tomé yo:**
  1. Usar "registro["campo"]" para los campos obligatorios ("ciudad", "tipo_turismo", "duracion_horas") y ".get()" para los opcionales, de modo que falten datos obligatorios provoque un error en lugar de guardarse mal.
  2. Mantener la lógica de las consultas en PostgreSQL ("COUNT", "FILTER", "GROUP BY") y no calcular en Python; además, "SELECT" con columnas explícitas (sin "SELECT *") para no exponer datos sensibles.

- **Un error o solución que descarté:** la primera versión del HTML usaba variables que no existían en mi ruta ("stats") y la IA había supuesto FastAPI; lo descarté y adapté el HTML a mis variables reales de Flask. Aprendí que el código generado hay que contrastarlo con el proyecto real. [Añadir otro si procede]
- **Qué código puedo explicar y demostrar:** "db.py" (parámetros con ":nombre", "CAST ... AS jsonb", "RETURNING id" + "scalar_one()", "engine.begin()" frente a "engine.connect()").
- **Qué sigue pendiente o limitado:**
  - No he cursado HTML, por lo que "analitica.html" depende en gran parte de la asistencia de la IA.
  - Aún estoy aprendiendo SQL en la asignatura de Bases de Datos.

**Declaración:** Confirmo que la memoria describe fielmente mis fuentes, la asistencia recibida, los cambios que introduje y mi aportación personal. [Sergio Gilabert Solaz/ 06/11/26]