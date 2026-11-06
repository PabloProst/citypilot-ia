"""Rutas del servicio Flask."""
from io import BytesIO

import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request, send_file

from app import db, llm
from app.db import ping_db
from app.orchestrator import procesar_solicitud, TIPOS_VALIDOS


def datos_validos(ciudad, tipo_turismo, duracion_horas):
    return ciudad != "" and tipo_turismo in TIPOS_VALIDOS and duracion_horas in {"2", "4", "6"}


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        try:
            ping_db()
            return jsonify(servicio="citypilot", estado="ok", db="ok")
        except Exception:
            return jsonify(servicio="citypilot", estado="degradado", db="error"), 503

    @app.post("/planificar")
    def planificar_html():
        ciudad = request.form.get("ciudad", "").strip()
        tipo_turismo = request.form.get("tipo_turismo", "")
        duracion_horas = request.form.get("duracion_horas", "")
        preferencias = request.form.get("preferencias", "")

        if not datos_validos(ciudad, tipo_turismo, duracion_horas):
            return render_template("resultado.html", error="Datos del formulario no válidos"), 400

        resultado = procesar_solicitud(ciudad, tipo_turismo, int(duracion_horas), preferencias)
        return render_template("resultado.html", duracion_horas=duracion_horas,
                               modo_modelo=llm.LLM_MODE, **resultado)

    @app.post("/api/planificar")
    def planificar_api():
        datos = request.get_json(silent=True) or {}
        ciudad = str(datos.get("ciudad", "")).strip()
        tipo_turismo = str(datos.get("tipo_turismo", ""))
        duracion_horas = str(datos.get("duracion_horas", ""))
        preferencias = str(datos.get("preferencias", ""))

        if not datos_validos(ciudad, tipo_turismo, duracion_horas):
            return jsonify(error="Datos no válidos: revisa ciudad, tipo_turismo y duracion_horas"), 400

        resultado = procesar_solicitud(ciudad, tipo_turismo, int(duracion_horas), preferencias)
        return jsonify(resultado), 200

    @app.get("/analitica")
    def analitica():
        totales = db.obtener_estadisticas()
        ultimas = db.obtener_ultimas_solicitudes(8)
        return render_template("analitica.html", totales=totales,
                               top_ciudades=totales["por_ciudad_y_tipo"][:5], ultimas=ultimas)

    @app.get("/analitica/grafico.png")
    def grafico():
        datos = db.obtener_estadisticas()["por_ciudad_y_tipo"][:5]
        etiquetas = [f'{d["ciudad"]}\n{d["tipo_turismo"]}' for d in datos]
        cantidades = [d["cantidad"] for d in datos]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(etiquetas, cantidades)
        ax.set_title("Peticiones por ciudad y tipo")

        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return send_file(buffer, mimetype="image/png")

    @app.get("/api/estadisticas")
    def estadisticas_api():
        return jsonify(db.obtener_estadisticas())

    return app


app = create_app()