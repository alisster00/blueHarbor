import sys
import time

sys.path.insert(0, "/var/www/html")

from app import create_app
from extensions import db
from models import User

USERS = [
    {
        "username": "admin",
        "password": "Adm1n_Blu3H4rb0r_24!",
        "role":     "admin",
        "email":    "admin@bharbor.dl",
    },
    {
        "username": "omar",
        "password": "DevOmar18!",
        "role":     "viewer",
        "email":    "omar@bharbor.dl",
    },
    {
        "username": "logistics",
        "password": "Log1st1cs#2024",
        "role":     "viewer",
        "email":    "logistics@bharbor.dl",
    },
]

def wait_for_db(app, retries=10, delay=3):
    """Espera a que PostgreSQL esté disponible."""
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError

    with app.app_context():
        for attempt in range(1, retries + 1):
            try:
                db.session.execute(text("SELECT 1"))
                print(f"[+] DB disponible (intento {attempt})")
                return True
            except OperationalError:
                print(f"[!] DB no disponible, reintentando ({attempt}/{retries})...")
                time.sleep(delay)
    return False

def seed(app):
    with app.app_context():
        db.create_all()
        for u_data in USERS:
            if not User.query.filter_by(username=u_data["username"]).first():
                u = User(
                    username=u_data["username"],
                    role=u_data["role"],
                    email=u_data["email"],
                )
                u.set_password(u_data["password"])
                db.session.add(u)
                print(f"[+] Usuario creado: {u_data['username']} ({u_data['role']})")
        db.session.commit()
        print("[+] Base de datos inicializada correctamente.")

if __name__ == "__main__":
    app = create_app()
    if wait_for_db(app):
        seed(app)
    else:
        print("[!] No se pudo conectar a la BD. Abortando.")
        sys.exit(1)
