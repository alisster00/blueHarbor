import os

class Config:
    # flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "flask-dev-key-not-for-prod")
    DEBUG = True

    # JWT
    # clave de baja entropía - presente en cualquier wordlist estándar.
    # combinada con el endpoint /debug expuesto, permite forjar tokens admin.
    JWT_SECRET    = os.environ.get("JWT_SECRET", "secret")
    JWT_ALGORITHM = "HS256"

    # base de datos
    DB_HOST     = os.environ.get("DB_HOST",     "db")
    DB_PORT     = os.environ.get("DB_PORT",     "5432")
    DB_NAME     = os.environ.get("DB_NAME",     "blueharbor")
    DB_USER     = os.environ.get("DB_USER",     "blueharbor")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "Str0ng_DB_P4ss!")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('DB_USER', 'blueharbor')}:"
        f"{os.environ.get('DB_PASSWORD', 'Str0ng_DB_P4ss!')}@"
        f"{os.environ.get('DB_HOST', 'db')}:"
        f"{os.environ.get('DB_PORT', '5432')}/"
        f"{os.environ.get('DB_NAME', 'blueharbor')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # app
    APP_VERSION = "1.0.0"
    COMPANY     = "BlueHarbor Solutions"
