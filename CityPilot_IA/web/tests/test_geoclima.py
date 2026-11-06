"""Tests de geocodificar y obtener_meteorologia con respuestas simuladas."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import api_clients


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_geocodificar_normaliza_campos(monkeypatch):
    datos = {"results": [{"name": "Valencia", "country": "España",
                          "latitude": 39.47, "longitude": -0.38,
                          "population": 800000}]}
    monkeypatch.setattr(api_clients.requests, "get",
                        lambda *a, **k: FakeResponse(datos))

    resultado = api_clients.geocodificar("Valencia")

    assert resultado == {"ciudad": "Valencia", "pais": "España",
                         "lat": 39.47, "lon": -0.38}


def test_geocodificar_sin_resultados_lanza_valueerror(monkeypatch):
    monkeypatch.setattr(api_clients.requests, "get",
                        lambda *a, **k: FakeResponse({}))

    with pytest.raises(ValueError):
        api_clients.geocodificar("CiudadQueNoExiste")


def test_meteorologia_normaliza_campos(monkeypatch):
    datos = {"current": {"time": "2026-11-06T12:00", "temperature_2m": 21.5,
                         "precipitation": 0.0, "weather_code": 1}}
    monkeypatch.setattr(api_clients.requests, "get",
                        lambda *a, **k: FakeResponse(datos))

    resultado = api_clients.obtener_meteorologia(39.47, -0.38)

    assert resultado == {"temperatura_c": 21.5, "precipitacion_mm": 0.0,
                         "codigo_tiempo": 1, "instante": "2026-11-06T12:00"}


def test_meteorologia_campo_ausente_no_se_convierte_en_cero(monkeypatch):
    datos = {"current": {"time": "2026-11-06T12:00", "temperature_2m": 21.5,
                         "weather_code": 1}}  # falta precipitation
    monkeypatch.setattr(api_clients.requests, "get",
                        lambda *a, **k: FakeResponse(datos))

    with pytest.raises(RuntimeError):
        api_clients.obtener_meteorologia(39.47, -0.38)