import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, render_template_string, current_app
from config import Config

admin_bp = Blueprint("admin", __name__)

# decoradores
def require_jwt(f):
    """Valida el JWT de la cabecera Authorization."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()

        if not token:
            return jsonify({
                "error": "Authorization header required",
                "hint":  "Format: Bearer <token>",
            }), 401

        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=[Config.JWT_ALGORITHM],
            )
            request.jwt_payload = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401

        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    """Verifica que el payload del JWT contenga role=admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload = getattr(request, "jwt_payload", {})
        role = payload.get("role")

        if role != "admin":
            return jsonify({
                "error":  "Admin role required",
                "yours":  role,
                "needed": "admin",
            }), 403

        return f(*args, **kwargs)
    return wrapper

# endpoints (panel de administración)
@admin_bp.route("/dashboard", methods=["GET"])
@require_jwt
@require_admin
def dashboard():
    """
    Admin Dashboard
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    description: Panel de administración. Requiere rol admin en el JWT.
    responses:
      200:
        description: Bienvenida y listado de endpoints admin
      401:
        description: Token ausente o inválido
      403:
        description: Privilegios insuficientes
    """
    user = request.jwt_payload.get("user")
    return jsonify({
        "message":   f"Welcome to the admin panel, {user}",
        "endpoints": [
            "GET  /api/v1/admin/dashboard",
            "GET  /api/v1/admin/users",
            "POST /api/v1/admin/report",
        ],
    })

@admin_bp.route("/users", methods=["GET"])
@require_jwt
@require_admin
def list_users():
    """
    List System Users
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    description: Devuelve todos los usuarios registrados en el sistema.
    responses:
      200:
        description: Lista de usuarios
      401:
        description: Token ausente o inválido
      403:
        description: Privilegios insuficientes
    """
    from models import User
    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]})

@admin_bp.route("/report", methods=["POST"])
@require_jwt
@require_admin
def generate_report():
    """
    Generate Personalized Report
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    description: >
      Genera un reporte personalizado usando un motor de templates dinamico.
      Soporta templates dinamicos para mensajes personalizados.
      Variables disponibles: recipient, company.
      Ejemplo - template: "Dear {{recipient}}, your shipment from {{company}} has arrived."
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            template:
              type: string
              example: "Dear {{recipient}}, your shipment from {{company}} has arrived."
            recipient:
              type: string
              example: "Ellen Joe"
    responses:
      200:
        description: Reporte renderizado
      400:
        description: Body ausente
      500:
        description: Error en el template (con stack trace si debug=true)
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    template  = data.get("template",  "No template provided.")
    recipient = data.get("recipient", "Valued Customer")

    try:
        rendered = render_template_string(
            template,
            recipient=recipient,
            company=Config.COMPANY,
        )
        return jsonify({
            "status":       "ok",
            "report":       rendered,
            "generated_by": request.jwt_payload.get("user"),
        })

    except Exception as exc:
        return jsonify({
            "status":  "error",
            "message": str(exc),
            "debug":   current_app.config.get("DEBUG", False),
        }), 500
