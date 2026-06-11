import datetime
import jwt
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, make_response,
)
from models import User
from config import Config

web_bp = Blueprint("web", __name__)

def _make_token(username: str, role: str) -> str:
    payload = {
        "user": username,
        "role": role,
        "iat":  datetime.datetime.utcnow(),
        "exp":  datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def _decode_token(token: str) -> dict:
    return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])

# páginas
@web_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("web.login_page"))

@web_bp.route("/login", methods=["GET"])
def login_page():
    error = request.args.get("error")
    return render_template("index.html", company=Config.COMPANY, error=error)

@web_bp.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = _make_token(user.username, user.role)
        dest  = "web.admin_panel" if user.role == "admin" else "web.user_dashboard"
        resp  = make_response(redirect(url_for(dest)))
        resp.set_cookie("token", token, httponly=True)
        return resp

    return redirect(url_for("web.login_page", error="Credenciales inválidas"))

@web_bp.route("/dashboard", methods=["GET"])
def user_dashboard():
    token = request.cookies.get("token", "")
    try:
        payload = _decode_token(token)
        return render_template(
            "dashboard.html",
            user=payload["user"],
            company=Config.COMPANY,
        )
    except Exception:
        return redirect(url_for("web.login_page"))

@web_bp.route("/admin", methods=["GET"])
def admin_panel():
    token = request.cookies.get("token", "")
    try:
        payload = _decode_token(token)
        if payload.get("role") != "admin":
            return redirect(url_for("web.login_page", error="Privilegios insuficientes"))
        return render_template(
            "admin.html",
            user=payload["user"],
            company=Config.COMPANY,
        )
    except Exception:
        return redirect(url_for("web.login_page"))

@web_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for("web.login_page")))
    resp.delete_cookie("token")
    return resp
