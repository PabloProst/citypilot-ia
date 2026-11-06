"""Acceso a PostgreSQL. Conexión mínima dada; funciones de negocio pendientes."""
import os
import json
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None


def ping_db():
    if engine is None:
        raise RuntimeError("Falta DATABASE_URL")
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar_one()


def guardar_solicitud(registro: dict) -> int:
    """TODO(ALUMNADO): INSERT parametrizado; devolver id de solicitud.

    La tabla existente es `solicitudes`. `registro` debe incluir: ciudad,
    pais, tipo_turismo, duracion_horas, preferencias, latitud, longitud,
    meteorologia, lugares, prompt_usado, itinerario, estado, duracion_ms,
    error_resumido, modo_demo y modo_modelo. Los diccionarios/listas van
    a columnas JSONB: podéis usar json.dumps(...) y CAST(:dato AS jsonb)
    o declarar el tipo JSONB en el parámetro enlazado.

    Pistas: with engine.begin() as conn; text(...); RETURNING id.
    Nunca concatenar strings de entrada dentro del SQL.
    """
    json_meteorologia = json.dumps(registro.get("meteorologia", {}))
    json_lugares = json.dumps(registro.get("lugares", []))

    with engine.begin() as conn:
        consulta = text("""
                INSERT INTO solicitudes(
                    ciudad, pais, tipo_turismo, duracion_horas, preferencias,
                    latitud, longitud, meteorologia, lugares,
                    prompt_usado, itinerario, modo_demo, modo_modelo,
                    estado, duracion_ms, error_resumido)
                 VALUES 
                    (:ciudad, :pais, :tipo_turismo, :duracion_horas, :preferencias,
                    :latitud, :longitud,
                    CAST(:meteorologia AS jsonb),
                    CAST(:lugares AS jsonb),
                    :prompt_usado, :itinerario, :modo_demo, :modo_modelo,
                    :estado, :duracion_ms, :error_resumido)
                RETURNING id""")
        
        return conn.execute(consulta, {
            "ciudad": registro["ciudad"],
            "pais": registro.get("pais"),
            "tipo_turismo": registro["tipo_turismo"],
            "duracion_horas": registro["duracion_horas"],
            "preferencias": registro.get("preferencias", ""),
            "latitud": registro.get("latitud"),
            "longitud": registro.get("longitud"),
            "meteorologia": json_meteorologia,
            "lugares": json_lugares,
            "prompt_usado": registro.get("prompt_usado"),
            "itinerario": registro.get("itinerario"),
            "modo_demo": registro.get("modo_demo", False),
            "modo_modelo": registro.get("modo_modelo"),
            "estado": registro.get("estado", "pendiente"),
            "duracion_ms": registro.get("duracion_ms"),
            "error_resumido": registro.get("error_resumido"),
        }).scalar_one()
                         

def obtener_estadisticas() -> dict:
    """TODO(ALUMNADO): total, agrupación por ciudad/tipo y nº errores."""
    with engine.connect() as conn:  
        totales = conn.execute(text("""
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE error_resumido IS NOT NULL) AS errores
            FROM solicitudes""")).mappings().one()

        grupos = conn.execute(text("""
            SELECT ciudad, tipo_turismo, COUNT(*) AS cantidad
            FROM solicitudes
            GROUP BY ciudad, tipo_turismo
            ORDER BY cantidad DESC
        """)).mappings().all()

    return {
        "total": totales["total"],
        "errores": totales["errores"],
        "por_ciudad_y_tipo": [dict(g) for g in grupos],
    }
    


def obtener_ultimas_solicitudes(limite: int = 8) -> list[dict]:
    """TODO(ALUMNADO): últimas solicitudes sin mostrar claves ni secretos."""

    with engine.connect() as conn:
        query = text("""
                SELECT id, fecha, ciudad, tipo_turismo, estado,
                    modo_demo, duracion_ms
                FROM solicitudes
                ORDER BY fecha DESC
                LIMIT :limite
            """)
        filas = conn.execute(query, {"limite": limite}).mappings().all()
        return [dict(f) for f in filas]
