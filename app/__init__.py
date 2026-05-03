from flask import Flask
from flask_migrate import Migrate

from app.models import db
from app.routes import bp
from config import Config


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa extensiones
    db.init_app(app)
    Migrate(app, db)

    # Registra blueprints
    app.register_blueprint(bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}, 200

    return app
