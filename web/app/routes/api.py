import sys
from flask import Blueprint, jsonify, current_app
from config import Config

api_bp = Blueprint("api", __name__)

@api_bp.route("/", methods=["GET"])
def status():
    """
    API Status
    ---
    tags:
      - General
    responses:
      200:
        description: Estado y versión de la API
        schema:
          properties:
            status:  {type: string}
            version: {type: string}
            company: {type: string}
            docs:    {type: string}
    """
    return jsonify({
        "status":  "ok",
        "version": Config.APP_VERSION,
        "company": Config.COMPANY,
        "docs":    "/api/v1/docs",
    })

@api_bp.route("/health", methods=["GET"])
def health():
    """
    Health Check
    ---
    tags:
      - General
    description: >
      Estado del sistema. Incluye información de diagnóstico para monitoreo.

      **Nota interna:** Pendiente de restringir a red interna antes del siguiente release.
    responses:
      200:
        description: Estado de salud del servicio
    """
    return jsonify({
        "status":      "ok",
        "env":         "production",
        "debug":       current_app.config["DEBUG"],
        "version":     Config.APP_VERSION,
        "python_path": sys.path,
        "server":      "gunicorn/22.0.0",
    })
