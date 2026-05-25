import os
from flask import current_app

def allowed_file(filename: str) -> bool:
    """Verifica que el archivo tenga una extensión permitida."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )

def ensure_upload_folder():
    """Crea la carpeta de uploads si no existe."""
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    return folder
