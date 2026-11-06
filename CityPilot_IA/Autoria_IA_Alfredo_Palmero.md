[Autoria_IA_Alfredo_Palmero.md](https://github.com/user-attachments/files/34473360/Autoria_IA_Alfredo_Palmero.md)
# Memoria de Uso de IA y Autoría - Punto Único de Integración

**Autor/a:** Alfredo Palmero
**Fecha:** 06/11/2026

## 1. Declaración general
He utilizado Inteligencia Artificial (Gemini como copiloto de contexto y Claude como revisor/confirmador) para comprender cómo implementar el flujo de `procesar_solicitud` a partir del esqueleto con los `TODO(ALUMNADO)`, entender las plantillas HTML y mejorar la estructura del código. Todo el código propuesto ha sido revisado, probado en local y adaptado a las restricciones del proyecto.

---

## 2. Resumen de Herramientas y Uso

| Herramienta | Versión | Propósito Principal | Fases / Archivos |
| :--- | :--- | :--- | :--- |
| **Gemini** | 2026 | Explicación del contexto y de las llamadas encadenadas a `api_clients` y `llm`. | `main.py` (puntos #2 y #4) |
| **Gemini** | 2026 | Explicación del registro y del `id` devuelto por `db.guardar_solicitud`. | `main.py` (punto #5) |
| **Gemini** | 2026 | Comprensión del HTML de las plantillas `index` y `resultado` (no sé HTML). | `templates/index.html`, `templates/resultado.html` |
| **Claude** | 2026 | Confirmación del diccionario `contexto` y revisión del registro final. | `main.py` |
| **Claude** | 2026 | Explicación y validación del uso de `time.perf_counter()` para `duracion_ms`. | `main.py` (punto #5) |
| **Claude** | 2026 | Mejora de la estructura y organización de `main.py`. | `main.py` |

---

## 3. Interacciones Sustantivas y Evolución del Desarrollo

### 3.1. Medición de la duración con `time` (`main.py`)
* **Contexto/Problema:** Sabía que tenía que usar la función `time` pero no sabía cómo se usaba para cubrir el campo "duración" del punto #5.
* **Prompt principal:** *"Explícame cómo funciona `time` y cómo podría usarlo para este contexto, donde tengo que medir la duración de `procesar_solicitud`."*
* **Respuesta/Sugerencias:** Claude explicó que `time.perf_counter()` es un contador de alta resolución pensado para medir intervalos (no para saber la hora, que sería `time.time()`, menos fiable). Se pone `inicio = time.perf_counter()` al empezar y se calcula `duracion_ms = int((time.perf_counter() - inicio) * 1000)` justo antes de construir el registro.
* **Decisiones:** Se incorporó tal cual, colocando `inicio` al principio de la función y el cálculo justo antes del diccionario `registro`. Añadí el `import time` (que no estaba en el original; lo puse por intuición y lo confirmé con Claude).
* **Trazabilidad:** `main.py`, campo `duracion_ms` del diccionario `registro`.

### 3.2. Punto #2: geocodificación y clima (`main.py`)
* **Contexto/Problema:** No sabía qué funciones de `api_clients` usar para el punto #2 ni en qué orden, al estar el esqueleto con `raise NotImplementedError`.
* **Prompt principal:** *"Para el punto #2 (geocodificar y consultar clima), ¿cómo se encadenan las funciones de `api_clients`? ¿Qué claves devuelve cada una?"*
* **Respuesta/Sugerencias:** Gemini explicó que primero se llama `geo = api_clients.geocodificar(ciudad)` (devuelve `lat`, `lon`, `ciudad`, `pais`) y después `meteorologia = api_clients.obtener_meteorologia(geo["lat"], geo["lon"])`. Me insistió en usar `geo["ciudad"]` (la normalizada) en lugar del string del usuario.
* **Decisiones:** Se incorporaron las dos líneas en ese orden y se reutilizaron `geo["ciudad"]`, `geo["pais"]`, `geo["lat"]` y `geo["lon"]` en el contexto y en el registro. Claude confirmó que el encadenamiento era correcto.
* **Trazabilidad:** `main.py`, bloque de geocodificación y clima.

### 3.3. Punto #4: contexto y `llm.generar_itinerario` (`main.py`)
* **Contexto/Problema:** No entendía qué era "el contexto" ni cómo se llamaba a `llm.generar_itinerario`, ni qué devolvía exactamente.
* **Prompt principal:** *"¿Qué claves debe llevar el contexto para el LLM y cómo se llama a `llm.generar_itinerario`? ¿Devuelve una cosa o dos?"*
* **Respuesta/Sugerencias:** Gemini explicó que el contexto es un diccionario Python con `ciudad`, `tipo_turismo`, `duracion_horas`, `preferencias`, `meteorologia` y `lugares`. La llamada es `itinerario, prompt = llm.generar_itinerario(contexto)`, que devuelve dos valores: el itinerario y el prompt usado (para trazabilidad). Me aclaró que el modelo **organiza** los lugares de Overpass, no los inventa.
* **Decisiones:** Se incorporó el diccionario `contexto` con esas seis claves y el desempaquetado de dos valores. Claude confirmó que el diccionario y el desempaquetado eran correctos.
* **Trazabilidad:** `main.py`, bloque de contexto y llamada al LLM.

### 3.4. Punto #5: registro y `db.guardar_solicitud` (`main.py`)
* **Contexto/Problema:** No sabía qué campos debía llevar el diccionario `registro` ni qué devolvía `db.guardar_solicitud`.
* **Prompt principal:** *"¿Qué campos necesita el registro de PostgreSQL y qué devuelve `db.guardar_solicitud`? ¿Cómo saco el `solicitud_id`?"*
* **Respuesta/Sugerencias:** Gemini agrupó los campos en cuatro bloques: entradas (`ciudad`, `pais`, `tipo_turismo`, `duracion_horas`, `preferencias`), APIs (`latitud`, `longitud`, `meteorologia`, `lugares`), LLM (`prompt_usado`, `itinerario`) y metadatos (`estado`, `duracion_ms`, `error_resumido`, `modo_demo`, `modo_modelo`). Me indicó que `db.guardar_solicitud(registro)` devuelve el `id` autogenerado, que se expone como `solicitud_id` en la salida.
* **Decisiones:** Se incorporó el diccionario `registro` completo y se guardó el retorno en `solicitud_id`, incluyéndolo en el contrato final. Claude revisó el registro antes de `db.guardar_solicitud` y confirmó que los campos coincidían con lo esperado.
* **Trazabilidad:** `main.py`, bloque de registro y llamada a `db.guardar_solicitud`.

### 3.5. Comprensión del HTML de las plantillas `index` y `resultado` (`templates/`)
* **Contexto/Problema:** No sé HTML y necesitaba entender qué hacían las plantillas `index.html` y `resultado.html` para saber cómo se conectaban con la ruta Flask y con el contrato devuelto por `procesar_solicitud`.
* **Prompt principal:** *"No sé HTML. Explícame qué hace este template de Flask, qué campos pinta y de dónde vienen los datos."*
* **Respuesta/Sugerencias:** Gemini explicó el papel de cada plantilla: `index.html` como formulario que envía los parámetros (`ciudad`, `tipo_turismo`, `duracion_horas`, `preferencias`) al endpoint, y `resultado.html` como plantilla que recibe el diccionario devuelto por `procesar_solicitud` y lo pinta con `{{ }}` y bucles `{% for %}`. Me señaló que los nombres de las claves del contrato (`ciudad`, `meteorologia`, `lugares`, `itinerario`, `modo_demo`, `solicitud_id`) deben coincidir con los que usa el template.
* **Decisiones:** No modifiqué el HTML (no era el objetivo); solo lo usé para verificar que el contrato de salida de `procesar_solicitud` coincidía con lo que esperaban las plantillas. Confirmé con Claude que las claves del contrato eran consistentes con el HTML.
* **Trazabilidad:** `templates/index.html`, `templates/resultado.html`, contrato de salida de `main.py`.

### 3.6. Mejora de la estructura de `main.py` (Claude)
* **Contexto/Problema:** Una vez implementado el flujo, `procesar_solicitud` había quedado funcional pero con bloques desordenados y poca separación entre validación, APIs, LLM y persistencia.
* **Prompt principal:** *"Revisa la estructura de `main.py` y propón una organización más clara por pasos sin cambiar la lógica."*
* **Respuesta/Sugerencias:** Claude propuso ordenar la función en bloques numerados y comentados (validación → geocodificación/clima → lugares → contexto/LLM → registro → contrato de salida), y mantener las constantes `TIPOS_VALIDOS` y `DURACIONES_VALIDAS` al principio del archivo.
* **Decisiones:** Se aceptó la reorganización por bloques, manteniendo intacta la lógica y los nombres de las funciones. Se validó ejecutando localmente que el contrato de salida no cambiaba.
* **Trazabilidad:** `main.py`, reorganización de `procesar_solicitud`.

---

## 4. Verificación Final
* No se han incluido tokens, contraseñas ni API Keys reales en los prompts proporcionados a la IA ni en los commits subidos a GitHub.
* El código final ha sido testeado manualmente y validado en el entorno de desarrollo antes de solicitar el Merge en los correspondientes Pull Requests.
* Todas las firmas de funciones (`api_clients`, `db`, `llm`) y las claves del contrato de salida se han contrastado con el código real del proyecto y con las plantillas HTML antes de incorporar las sugerencias.
