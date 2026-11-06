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
    # Mapeo seguro de categorías a etiquetas de OpenStreetMap (Overpass QL)
    filtros_seguros = {
        "cultural": 'nwr["tourism"~"museum|gallery|artwork|attraction"]',
        "gastronomica": 'nwr["amenity"~"restaurant|cafe|bar"]',
        "naturaleza": 'nwr["leisure"~"park|garden|nature_reserve"]',
        "familiar": 'nwr["leisure"~"playground|water_park"]'
    }
    
    filtro_ql = filtros_seguros.get(tipo, 'nwr["tourism"]')
    
    # Construimos la consulta con un radio de 2000m (2km)
    query = f"""
    [out:json][timeout:10];
    (
      {filtro_ql}(around:2000,{lat},{lon});
    );
    out center;
    """
    
    response = requests.post(OVERPASS_URL, data={'data': query}, timeout=10)
    
    if response.status_code != 200:
        print(f"Error al consultar Overpass. Código de estado: {response.status_code}")
        return []
        
    data = response.json()
    elementos = data.get("elements", [])
    lugares_normalizados = []
    
    for el in elementos:
        tags = el.get("tags", {})
        nombre = tags.get("name")
        
        if nombre:
            lugar_lat = el.get("lat")
            lugar_lon = el.get("lon")
            
            if lugar_lat is None and "center" in el:
                lugar_lat = el["center"].get("lat")
                lugar_lon = el["center"].get("lon")
                
            if lugar_lat is not None and lugar_lon is not None:
                lugar_limpio = {
                    "nombre": nombre,
                    "categoria": tipo,
                    "lat": lugar_lat,
                    "lon": lugar_lon,
                    "fuente": "Overpass API"
                }
                lugares_normalizados.append(lugar_limpio)
                
        if len(lugares_normalizados) >= 12:
            break
            
    return lugares_normalizados


def cargar_fixture_lugares() -> list[dict]:
    """Utilidad entregada para simular Overpass durante pruebas sin Internet.

    Los lugares son FICTICIOS y deben identificarse como DEMO en la UI.
    """
    file_path = Path("/fixtures/puntos_demo.json")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parents[2] / "fixtures/puntos_demo.json"
    return json.loads(file_path.read_text(encoding="utf-8"))["lugares"]