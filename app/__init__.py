from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text

from app.models import db
from app.routes import bp
from app.auth_routes import auth_bp
from config import Config


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa extensiones
    db.init_app(app)
    Migrate(app, db)

    # CORS — permite peticiones del frontend (Vite dev server)
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

    # Registra blueprints
    app.register_blueprint(bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Habilitar la extensión pgvector en PostgreSQL
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            app.logger.warning("No se pudo crear extensión pgvector: %s", e)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}, 200

    return app
