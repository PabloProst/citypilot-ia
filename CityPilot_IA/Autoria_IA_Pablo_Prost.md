# Memoria de Uso de IA y Autoría - CityPilot_IA

**Autor/a:** Pablo Prost
**Fecha:** 06/11/2026

## 1. Declaración general
He utilizado Inteligencia Artificial (Gemini) como copiloto de desarrollo para la resolución de dudas de sintaxis, diseño del prompt de Cohere, tests con mocks y asistencia en conflictos de Git. Todo el código propuesto ha sido revisado, probado en local y adaptado a las restricciones del proyecto.

---

## 2. Resumen de Herramientas y Uso

| Herramienta | Versión | Propósito Principal | Fases / Archivos |
| :--- | :--- | :--- | :--- |
| **Gemini** | 2026 | Sintaxis Overpass QL, parseo JSON, `if` vs `try/except`. | `api_clients.py` |
| **Gemini** | 2026 | Setup de tests con `@patch` y objetos `Mock()`. | `tests/test_smoke.py` |
| **Gemini** | 2026 | Diseño de prompt estructurado, manejo de errores 401/429. | `llm.py` |
| **Gemini** | 2026 | Resolución de conflictos: `stash`, `pull`, `reset`, `push --force`.| Terminal / GitHub (PR 1 y 2) |
| **Gemini** | 2026 | Estructuración y formato de esta propia memoria en Markdown. | `MEMORIA_IA_Pablo_Prost.md` |

---

## 3. Interacciones Sustantivas y Evolución del Desarrollo

### 3.1. Implementación de Overpass API (`api_clients.py`)
* **Contexto/Problema:** Necesitaba consultar la API de Overpass filtrando por categorías específicas en un radio de 2km, normalizar la respuesta y manejar la diferencia entre nodos y vías (`center`).
* **Prompt principal:** *"Genera el código para obtener_lugares usando Overpass QL normalizando los datos. Condición: usar solo código visto en clase y extraer lat/lon según sea nodo o vía."*
* **Respuesta/Sugerencias:** El modelo generó la consulta QL estructurada (`around:2000`) y un diccionario de mapeo seguro para evitar inyecciones. Para la respuesta, propuso comprobar `if response.status_code != 200`.
* **Decisiones (Qué se incorporó/descartó):** Se incorporó la lógica del mapeo seguro y la normalización del JSON. Descarté algunas variables innecesarias del modelo inicial para hacerlo más conciso y asegurar que el límite de 12 lugares se cumpliera con un `break`.
* **Trazabilidad:** Comprobado mediante ejecución local y test unitario. Subido en el **Commit:** `feat: implementar obtener_lugares con Overpass y test`. (PR 1).

### 3.2. Pruebas Unitarias con Mocks (`test_smoke.py`)
* **Contexto/Problema:** Necesitaba probar la función `obtener_lugares` sin hacer peticiones reales a la API de Overpass para no depender de internet en los tests.
* **Prompt principal:** *"Proporciona el test unitario para la función de Overpass simulando una respuesta 200 y una lista con un nodo y un way."*
* **Respuesta/Sugerencias:** La IA proporcionó el uso del decorador `@patch('app.api_clients.requests.post')` y la configuración de un objeto `Mock()` que devuelve un JSON estático.
* **Decisiones:** Incorporado íntegramente. Se validó ejecutando pytest, comprobando que la función parsea correctamente el `center` de las vías y el `lat/lon` de los nodos.
* **Trazabilidad:** Archivo `web/tests/test_smoke.py`, incluido en el PR 1.

### 3.3. Evolución del Prompt y API de Cohere (`llm.py`)
* **Contexto/Problema:** Había que diseñar un prompt para la API Cohere Chat v2 que generara un itinerario respetando límites de tiempo, clima y forzando a elegir solo lugares del listado extraído por la API, sin inventar datos.
* **Evolución del Prompt:**
  * *Primer intento (Básico):* "Crea un itinerario de {duracion_horas} horas para {ciudad} usando los siguientes lugares: {lugares}. Ten en cuenta este clima: {meteorologia}. No inventes cosas."
  * *Problema detectado:* El modelo a veces ignoraba la lluvia o se inventaba horarios de apertura que no existían en el JSON original de Overpass.
  * *Intervención IA:* Pedí a Gemini *"Ideas para restringir un prompt para que un modelo de IA no alucine (invente) horarios o ubicaciones."*
  * *Solución (Prompt Final):* El modelo sugirió estructurar el prompt con secciones en mayúsculas (`METEOROLOGÍA ACTUAL`, `REGLAS QUE DEBES CUMPLIR OBLIGATORIAMENTE`) y añadir condicionales estrictos (ej. "Si la lista tiene menos de 3 opciones, avisa al usuario").
* **Decisiones sobre el código:** En la llamada a `requests.post` hacia Cohere, la IA me guio para comprobar manualmente los errores 401 (falta de API key) y 429 (Rate limit) usando condicionales `if response.status_code == 401`, en lugar de capturar excepciones genéricas, cumpliendo las normas de la asignatura.
* **Trazabilidad:** **Commit:** `feat: integrar Cohere Chat v2 y prompt robusto`. (PR 2).

### 3.4. Resolución de Conflictos en Git / GitHub
* **Contexto/Problema:** Durante la integración del PR 1, tuve errores como `failed to push some refs` por diferencias de nombres de ramas (`overpass-lugares` vs `feature/overpass-lugares-b`) y un error de `Fast-forward aborted` al hacer `pull` desde `master` debido a cambios locales no confirmados. Además, accidentalmente hice un push directo a `master`.
* **Prompt principal:** *"Qué hago si hice pull y hay conflictos con master"* / *"Hice push directo a master y no se hizo el PR, cómo lo arreglo"*.
* **Respuesta/Sugerencias:** La IA explicó paso a paso el uso de `git stash` para guardar cambios temporalmente. Para deshacer el push erróneo a master, recomendó retroceder con `git reset --hard HEAD~1` y forzar la sincronización remota con `git push origin master --force`, y luego crear el PR desde la rama correcta.
* **Decisiones:** Ejecuté la secuencia de comandos indicada tras comprender qué hacía cada uno, logrando recuperar la integridad de la rama `master`, sincronizar el trabajo de mi compañero (Persona A) y dejar mi PR 1 correctamente abierto para revisión.

### 3.5. Redacción y Formato de la Memoria de IA
* **Contexto/Problema:** Necesitaba adaptar el registro de uso de IA al formato estricto exigido por la rúbrica de la asignatura (narrativa de problema, prompt, solución, descartes y trazabilidad).
* **Prompt principal:** *"Estructura la memoria documentando la evolución del prompt y los fragmentos de código, aplicando formato Markdown con '#' y tablas."*
* **Respuesta/Sugerencias:** La IA estructuró la narrativa en bloques lógicos, generó una tabla resumen inicial y aplicó las etiquetas de formato Markdown correctas.
* **Decisiones:** Se aceptó el formato propuesto, validando que reflejara fielmente el proceso real de desarrollo y aprendizaje de la actividad.

---

## 4. Verificación Final
* No se han incluido tokens, contraseñas ni API Keys reales en los prompts proporcionados a la IA ni en los commits subidos a GitHub.
* El código final ha sido testeado manualmente y validado en el entorno de desarrollo antes de solicitar el Merge en los correspondientes Pull Requests.