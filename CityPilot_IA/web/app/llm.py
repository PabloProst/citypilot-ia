"""Adaptador Cohere. El PROMPT lo redacta el alumnado."""
import os
import json
import requests

LLM_MODE = os.getenv("LLM_MODE", "mock").lower()
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r7b-12-2024")


def generar_itinerario(contexto: dict) -> tuple[str, str]:
    """Devuelve (texto_itinerario, prompt_usado).

    `contexto` incluye: ciudad, tipo_turismo, duracion_horas,
    preferencias, meteorologia y lista de lugares REALES de la fuente.
    """
    if LLM_MODE == "mock":
        return _simulador(contexto), "[SIMULADOR: sin llamada a modelo]"

    if LLM_MODE != "cohere":
        raise ValueError("LLM_MODE debe ser 'mock' o 'cohere'")

    api_key = os.getenv("COHERE_API_KEY", "")
    if not api_key:
        raise RuntimeError("Falta COHERE_API_KEY (pedirla al docente)")

    # 1. Extracción de datos del contexto para el prompt
    lugares_reales = contexto.get("lugares", [])
    lugares_str = json.dumps(lugares_reales, ensure_ascii=False, indent=2)
    clima = contexto.get("meteorologia", {})
    temp = clima.get("temperatura_c", "Desconocida")
    precip = clima.get("precipitacion_mm", "0.0")

    # 2. PROMPT DISEÑADO (Versión Mejorada)
    prompt = f"""
    Actúa como un guía turístico experto y crea un itinerario para la ciudad de {contexto.get('ciudad')}.
    
    PARÁMETROS DEL VIAJE:
    - Duración: {contexto.get('duracion_horas')} horas.
    - Tipo de turismo: {contexto.get('tipo_turismo')}.
    - Preferencias adicionales del usuario: {contexto.get('preferencias', 'Ninguna específica')}.
    
    METEOROLOGÍA ACTUAL:
    - Temperatura: {temp}°C.
    - Precipitación: {precip}mm.
    
    LISTA ESTRICTA DE LUGARES DISPONIBLES:
    {lugares_str}
    
    REGLAS QUE DEBES CUMPLIR OBLIGATORIAMENTE:
    1. Escoge únicamente entre 3 y 5 lugares de la LISTA ESTRICTA DE LUGARES DISPONIBLES. 
    2. NO inventes lugares, direcciones, ni horarios de apertura bajo ningún concepto.
    3. Si la lista de lugares tiene menos de 3 opciones, incluye un mensaje al principio indicando claramente: "No hay suficientes datos disponibles para hacer un itinerario completo, pero te sugiero lo siguiente con la información que tengo:".
    4. Justifica brevemente el orden de la ruta y cómo se adapta al clima (por ejemplo, si la precipitación es mayor a 1mm, prioriza interiores o recomienda llevar paraguas).
    5. Respeta el límite de tiempo total de {contexto.get('duracion_horas')} horas.
    """

    # 3. Llamada a la API Chat v2 de Cohere
    url = "https://api.cohere.com/v2/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": COHERE_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        # 4. Comprobación de errores requerida
        if response.status_code == 401:
            raise RuntimeError("Error 401: Clave de API (COHERE_API_KEY) inválida o no autorizada.")
        elif response.status_code == 429:
            raise RuntimeError("Error 429: Rate limit superado. Demasiadas peticiones a Cohere.")
        elif response.status_code != 200:
            raise RuntimeError(f"Error {response.status_code} al consultar Cohere: {response.text}")
            
        data = response.json()
        
        # Extracción de la respuesta en Cohere v2
        try:
            texto_respuesta = data["message"]["content"][0]["text"]
        except (KeyError, IndexError):
            texto_respuesta = ""
            
        if not texto_respuesta.strip():
            raise RuntimeError("Error: Cohere devolvió una respuesta vacía.")
            
        return texto_respuesta, prompt

    except requests.exceptions.Timeout:
        raise RuntimeError("Error Timeout: La petición a Cohere superó el límite de tiempo.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error de conexión con Cohere: {str(e)}")


def _simulador(contexto: dict) -> str:
    """Salida no generativa para pruebas y para cuando no hay credenciales."""
    lugares = contexto.get("lugares") or []
    ciudad = contexto.get("ciudad", "la ciudad")
    tipo = contexto.get("tipo_turismo", "libre")
    nombres = [x.get("nombre", "Lugar sin nombre") for x in lugares[:4]]
    visitas = "\n".join(f"{i}. {nombre}" for i, nombre in enumerate(nombres, 1))
    if not visitas:
        visitas = "No hay lugares verificados disponibles."
    return f"[MODO SIMULACIÓN - NO ES IA]\nPlan {tipo} en {ciudad}:\n{visitas}"