"""Pruebas básicas proporcionadas. Completar con 2 tests más por pareja."""
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import create_app
from app.api_clients import obtener_lugares


def test_inicio_responde():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"CityPilot" in response.data


def test_analitica_responde():
    client = create_app().test_client()
    assert client.get("/analitica").status_code == 200

# tests para obtener_lugares y cargar_fixture_lugares

@patch("app.api_clients.requests.post")
def test_obtener_lugares_normaliza_datos(mock_post):
    """Test propio Persona B: Verifica el procesamiento de Overpass."""
    mock_respuesta = Mock()
    mock_respuesta.status_code = 200
    mock_respuesta.json.return_value = {
        "elements": [
            {
                "type": "node",
                "id": 101,
                "lat": 39.4700,
                "lon": -0.3760,
                "tags": {"name": "Restaurante de Prueba", "amenity": "restaurant"}
            },
            {
                "type": "way",
                "id": 102,
                "center": {"lat": 39.4710, "lon": -0.3770},
                "tags": {"name": "Parque Central", "leisure": "park"}
            }
        ]
    }
    mock_post.return_value = mock_respuesta

    resultados = obtener_lugares(lat=39.47, lon=-0.37, tipo="gastronomica")

    assert len(resultados) == 2
    assert resultados[0]["nombre"] == "Restaurante de Prueba"
    assert resultados[1]["lat"] == 39.4710

# Test extra sugerido: validación de entrada vacía en la API

def test_ciudad_vacia_produce_400():
    client = create_app().test_client()
    # Hacemos un POST al endpoint de planificación con ciudad vacía
    response = client.post("/api/planificar", json={"ciudad": "", "tipo_turismo": "cultural"})
    
    assert response.status_code == 400