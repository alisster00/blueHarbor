import datetime
import jwt
from flask import Blueprint, request, jsonify
from models import User
from config import Config

auth_bp = Blueprint("auth", __name__)

# helpers
def _make_token(username: str, role: str) -> str:
    payload = {
        "user": username,
        "role": role,
        "iat":  datetime.datetime.utcnow(),
        "exp":  datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

# endpoints
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username: {type: string, example: admin}
            password: {type: string, example: mypassword}
    responses:
      200:
        description: JWT token válido
        schema:
          properties:
            token: {type: string}
            user:  {type: string}
            role:  {type: string}
      400:
        description: Body inválido
      401:
        description: Credenciales incorrectas
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = _make_token(user.username, user.role)
    return jsonify({"token": token, "user": user.username, "role": user.role})

@auth_bp.route("/debug", methods=["GET"])
def debug_token():
    """
    [DEPRECATED] Debug Token Generator — DO NOT USE IN PRODUCTION
    ---
    tags:
      - Authentication
    description: >
      Genera un token de tipo *viewer* para pruebas de integración.

      **DEPRECATED:** Este endpoint fue marcado para eliminación en el
      sprint de hardening. Olvidaron desactivarlo antes del despliegue.

      El token está firmado con la misma `JWT_SECRET` usada en producción.
    responses:
      200:
        description: Token de invitado para testing
        schema:
          properties:
            message:   {type: string}
            token:     {type: string}
            algorithm: {type: string}
            _note:     {type: string}
    """
    token = _make_token("guest_debug", "viewer")

    return jsonify({
        "message":   "Debug token generated — remove this endpoint before go-live!",
        "token":     token,
        "algorithm": Config.JWT_ALGORITHM,
        "_note":     "Signed with the production JWT_SECRET env variable.",
    })
