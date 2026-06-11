from flask import Flask
from flasgger import Swagger
from config import Config
from extensions import db

# configuración de Swagger UI
SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint":     "apispec",
            "route":        "/api/v1/docs/apispec.json",
            "rule_filter":  lambda rule: True,
            "model_filter": lambda tag:  True,
        }
    ],
    "swagger_ui":        True,
    "specs_route":       "/api/v1/docs",
    "static_url_path":   "/flasgger_static",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title":       "BlueHarbor Internal API",
        "description": "API interna de gestión de envíos — BlueHarbor Solutions v1.0",
        "version":     "1.0.0",
        "contact":     {"name": "dev-team@bharbor.dl"},
    },
    "basePath": "/",
    "schemes":  ["http"],
    "securityDefinitions": {
        "Bearer": {
            "type":        "apiKey",
            "name":        "Authorization",
            "in":          "header",
            "description": "JWT token. Formato: Bearer <token>",
        }
    },
}

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # extensiones
    db.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # blueprints
    from routes.web   import web_bp
    from routes.api   import api_bp
    from routes.auth  import auth_bp
    from routes.admin import admin_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp,   url_prefix="/api/v1")
    app.register_blueprint(auth_bp,  url_prefix="/api/v1/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
