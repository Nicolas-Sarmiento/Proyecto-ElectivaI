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
    # Weaviate Cloud Configuration
    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
