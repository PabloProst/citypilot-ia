"""Punto ÚNICO de integración para web y API JSON."""
import time
from app import api_clients, db, llm

TIPOS_VALIDOS = {"cultural", "gastronomica", "naturaleza", "familiar"}
DURACIONES_VALIDAS = {2, 4, 6}


def procesar_solicitud(ciudad: str, tipo_turismo: str, duracion_horas: int, preferencias: str = "") -> dict:
    inicio = time.perf_counter()
    modo_demo = False

    # 1) Validación
    ciudad = ciudad.strip()
    duracion_horas = int(duracion_horas)
    if ciudad == "":
        raise ValueError("La ciudad es obligatoria")
    if tipo_turismo not in TIPOS_VALIDOS:
        raise ValueError("Tipo de turismo no válido")
    if duracion_horas not in DURACIONES_VALIDAS:
        raise ValueError("Duración no válida")

    # 2) Geocodificación y clima
    geo = api_clients.geocodificar(ciudad)
    meteorologia = api_clients.obtener_meteorologia(geo["lat"], geo["lon"])

    # 3) Lugares (si no hay, usar fixture)
    lugares = api_clients.obtener_lugares(geo["lat"], geo["lon"], tipo_turismo)
    if not lugares:
        lugares = api_clients.cargar_fixture_lugares()
        modo_demo = True

    # 4) Contexto y LLM
    contexto = {
        "ciudad": geo["ciudad"],
        "tipo_turismo": tipo_turismo,
        "duracion_horas": duracion_horas,
        "preferencias": preferencias,
        "meteorologia": meteorologia,
        "lugares": lugares,
    }
    itinerario, prompt = llm.generar_itinerario(contexto)

    # 5) Guardar en PostgreSQL
    duracion_ms = int((time.perf_counter() - inicio) * 1000)
    registro = {
        "ciudad": geo["ciudad"],
        "pais": geo["pais"],
        "tipo_turismo": tipo_turismo,
        "duracion_horas": duracion_horas,
        "preferencias": preferencias,
        "latitud": geo["lat"],
        "longitud": geo["lon"],
        "meteorologia": meteorologia,
        "lugares": lugares,
        "prompt_usado": prompt,
        "itinerario": itinerario,
        "estado": "ok",
        "duracion_ms": duracion_ms,
        "error_resumido": None,
        "modo_demo": modo_demo,
        "modo_modelo": llm.LLM_MODE,
    }
    solicitud_id = db.guardar_solicitud(registro)

    # 6) Devolver contrato
    return {
        "ciudad": geo["ciudad"],
        "tipo_turismo": tipo_turismo,
        "meteorologia": meteorologia,
        "lugares": lugares,
        "itinerario": itinerario,
        "modo_demo": modo_demo,
        "solicitud_id": solicitud_id,
    }