import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base de la aplicación."""

    # Construcción de la URI de conexión a partir de variables de entorno
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "editorial_db")
    DB_USER = os.getenv("DB_USER", "editorial_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "editorial_pass")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Almacenamiento de archivos PDF
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {"pdf"}

    # Keycloak — validación de Bearer tokens
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8082")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "editorial")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "editorial-backend")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

    @classmethod
    def keycloak_jwks_uri(cls) -> str:
        """URI del endpoint JWKS de Keycloak para obtener claves públicas."""
        return f"{cls.KEYCLOAK_URL}/realms/{cls.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    # Embeddings — modelo local con sentence-transformers
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    EMBEDDING_DIMENSION = 384
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
