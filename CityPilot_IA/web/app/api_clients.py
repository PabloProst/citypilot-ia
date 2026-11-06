"""Clientes HTTP de datos públicos. Se entregan los contratos, NO la solución."""
import json
import os
from pathlib import Path
import requests

GEO_URL = os.getenv("OPEN_METEO_GEO_URL", "https://geocoding-api.open-meteo.com/v1/search")
METEO_URL = os.getenv("OPEN_METEO_WEATHER_URL", "https://api.open-meteo.com/v1/forecast")
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")


def geocodificar(ciudad: str) -> dict:
    params = {
        "name": ciudad,
        "count": 1,
        "language": "es",
        "countryCode": "ES",
    }
    r = requests.get(GEO_URL, params=params, timeout=8)
    r.raise_for_status()

    resultados = r.json().get("results")
    if not resultados:
        raise ValueError(f"No se encontró la ciudad '{ciudad}'")

    primero = resultados[0]
    lat, lon = primero.get("latitude"), primero.get("longitude")
    if lat is None or lon is None:
        raise ValueError(f"Sin coordenadas para '{ciudad}'")

    return {
        "ciudad": primero.get("name", ciudad),
        "pais": primero.get("country", "España"),
        "lat": float(lat),
        "lon": float(lon),
    }


def obtener_meteorologia(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation,weather_code",
        "timezone": "auto",
    }
    r = requests.get(METEO_URL, params=params, timeout=8)
    r.raise_for_status()

    actual = r.json().get("current")
    if not actual:
        raise RuntimeError("Open-Meteo no devolvió condiciones actuales")

    campos = ("temperature_2m", "precipitation", "weather_code", "time")
    faltan = [c for c in campos if actual.get(c) is None]
    if faltan:
        raise RuntimeError(f"Faltan campos meteorológicos: {faltan}")

    return {
        "temperatura_c": float(actual["temperature_2m"]),
        "precipitacion_mm": float(actual["precipitation"]),
        "codigo_tiempo": int(actual["weather_code"]),
        "instante": str(actual["time"]),
    }


def obtener_lugares(lat: float, lon: float, tipo: str) -> list[dict]:
    """TODO(ALUMNADO).

    Consultar un radio urbano acotado de Overpass/OSM (2-3 km).
    Filtrar según tipo: cultural, gastronomica, naturaleza, familiar.
    Normalizar a [{nombre, categoria, lat, lon, fuente, ...}], máximo
    8-12 lugares. Gestionar nodos (lat/lon) y ways/relations (center).
    Nunca introducir valores libres del usuario en una consulta QL.
    """
    raise NotImplementedError("Implementa consulta de puntos de interés")


def cargar_fixture_lugares() -> list[dict]:
    """Utilidad entregada para simular Overpass durante pruebas sin Internet.

    Los lugares son FICTICIOS y deben identificarse como DEMO en la UI.
    """
    file_path = Path("/fixtures/puntos_demo.json")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parents[2] / "fixtures/puntos_demo.json"
    return json.loads(file_path.read_text(encoding="utf-8"))["lugares"]
