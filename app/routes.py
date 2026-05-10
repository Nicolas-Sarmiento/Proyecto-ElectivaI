import os
import uuid as uuid_lib
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from app.auth import require_auth
from app.models import Author, Organization, Publication, PublicationType, db

bp = Blueprint("main", __name__)


# ─── Utilidades ───────────────────────────────────────────────────────────────

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


# ─── Organizations ────────────────────────────────────────────────────────────

@bp.route("/organizations", methods=["GET"])
def list_organizations():
    """Lista todas las organizaciones."""
    orgs = Organization.query.order_by(Organization.name).all()
    return jsonify([o.to_dict() for o in orgs]), 200


@bp.route("/organizations/<string:org_id>", methods=["GET"])
def get_organization(org_id):
    """Obtiene una organización por ID."""
    org = db.get_or_404(Organization, org_id)
    return jsonify(org.to_dict()), 200


@bp.route("/organizations", methods=["POST"])
@require_auth
def create_organization():
    """Crea una nueva organización."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "El campo 'name' es requerido."}), 400

    org = Organization(name=data["name"])
    db.session.add(org)
    db.session.commit()
    return jsonify(org.to_dict()), 201


@bp.route("/organizations/<string:org_id>", methods=["PUT"])
@require_auth
def update_organization(org_id):
    """Actualiza el nombre de una organización."""
    org = db.get_or_404(Organization, org_id)
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "El campo 'name' es requerido."}), 400

    org.name = data["name"]
    db.session.commit()
    return jsonify(org.to_dict()), 200


@bp.route("/organizations/<string:org_id>", methods=["DELETE"])
@require_auth
def delete_organization(org_id):
    """Elimina una organización."""
    org = db.get_or_404(Organization, org_id)
    db.session.delete(org)
    db.session.commit()
    return jsonify({"message": "Organización eliminada correctamente."}), 200


# ─── Publication Types ─────────────────────────────────────────────────────────

@bp.route("/publication-types", methods=["GET"])
def list_publication_types():
    """Lista todos los tipos de publicación."""
    types = PublicationType.query.order_by(PublicationType.type_name).all()
    return jsonify([t.to_dict() for t in types]), 200


@bp.route("/publication-types/<string:type_id>", methods=["GET"])
def get_publication_type(type_id):
    """Obtiene un tipo de publicación por ID."""
    pub_type = db.get_or_404(PublicationType, type_id)
    return jsonify(pub_type.to_dict()), 200


@bp.route("/publication-types", methods=["POST"])
@require_auth
def create_publication_type():
    """Crea un nuevo tipo de publicación."""
    data = request.get_json()
    if not data or not data.get("type_name"):
        return jsonify({"error": "El campo 'type_name' es requerido."}), 400

    pub_type = PublicationType(type_name=data["type_name"])
    db.session.add(pub_type)
    db.session.commit()
    return jsonify(pub_type.to_dict()), 201


@bp.route("/publication-types/<string:type_id>", methods=["DELETE"])
@require_auth
def delete_publication_type(type_id):
    """Elimina un tipo de publicación."""
    pub_type = db.get_or_404(PublicationType, type_id)
    db.session.delete(pub_type)
    db.session.commit()
    return jsonify({"message": "Tipo de publicación eliminado correctamente."}), 200


# ─── Authors ──────────────────────────────────────────────────────────────────

@bp.route("/authors", methods=["GET"])
def list_authors():
    """Lista todos los autores."""
    authors = Author.query.order_by(Author.last_name, Author.first_name).all()
    return jsonify([a.to_dict() for a in authors]), 200


@bp.route("/authors/<string:author_id>", methods=["GET"])
def get_author(author_id):
    """Obtiene un autor por ID."""
    author = db.get_or_404(Author, author_id)
    return jsonify(author.to_dict()), 200


@bp.route("/authors", methods=["POST"])
@require_auth
def create_author():
    """
    Crea un nuevo autor.
    Body JSON:
        first_name (str, requerido)
        last_name  (str, requerido)
        orcid_url  (str, opcional)
        country    (str, opcional)
        organization_id (UUID str, opcional)
    """
    data = request.get_json()
    if not data or not data.get("first_name") or not data.get("last_name"):
        return jsonify({"error": "Los campos 'first_name' y 'last_name' son requeridos."}), 400

    author = Author(
        first_name=data["first_name"],
        last_name=data["last_name"],
        orcid_url=data.get("orcid_url"),
        country=data.get("country"),
        organization_id=data.get("organization_id"),
    )
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201


@bp.route("/authors/<string:author_id>", methods=["PUT"])
@require_auth
def update_author(author_id):
    """
    Actualiza los datos de un autor.
    Solo se actualizan los campos presentes en el body.
    """
    author = db.get_or_404(Author, author_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Body vacío."}), 400

    if "first_name" in data:
        author.first_name = data["first_name"]
    if "last_name" in data:
        author.last_name = data["last_name"]
    if "orcid_url" in data:
        author.orcid_url = data["orcid_url"]
    if "country" in data:
        author.country = data["country"]
    if "organization_id" in data:
        author.organization_id = data["organization_id"]

    db.session.commit()
    return jsonify(author.to_dict()), 200


@bp.route("/authors/<string:author_id>", methods=["DELETE"])
@require_auth
def delete_author(author_id):
    """Elimina un autor."""
    author = db.get_or_404(Author, author_id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "Autor eliminado correctamente."}), 200


# ─── Publications ─────────────────────────────────────────────────────────────

@bp.route("/publications", methods=["GET"])
def list_publications():
    """
    Lista todas las publicaciones.
    Query params opcionales:
        keyword (str): Filtra publicaciones que contengan esta palabra clave.
    """
    keyword = request.args.get("keyword")
    query = Publication.query

    if keyword:
        # Filtra publicaciones cuyo array keywords contenga el término (case-insensitive)
        query = query.filter(
            Publication.keywords.any(keyword)
        )

    publications = query.order_by(Publication.title).all()
    return jsonify([p.to_dict() for p in publications]), 200


@bp.route("/publications/<string:pub_id>", methods=["GET"])
def get_publication(pub_id):
    """Obtiene una publicación por ID."""
    pub = db.get_or_404(Publication, pub_id)
    return jsonify(pub.to_dict()), 200


@bp.route("/publications", methods=["POST"])
@require_auth
def create_publication():
    """
    Crea una nueva publicación con un archivo PDF adjunto.
    Usa multipart/form-data:
        title       (str, requerido)
        type_id     (UUID str, opcional)
        publish_date (str ISO, opcional, ej: '2024-01-15')
        keywords    (str, repetido para múltiples valores)
        author_ids  (UUID str, repetido para múltiples autores)
        file        (archivo PDF, requerido)
    """
    # Validar campos requeridos
    title = request.form.get("title")
    if not title:
        return jsonify({"error": "El campo 'title' es requerido."}), 400

    # Validar archivo PDF
    if "file" not in request.files:
        return jsonify({"error": "Se requiere un archivo PDF (campo 'file')."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Solo se permiten archivos PDF."}), 400

    # Guardar el archivo con nombre único para evitar colisiones
    upload_folder = ensure_upload_folder()
    original_name = secure_filename(file.filename)
    unique_filename = f"{uuid_lib.uuid4()}_{original_name}"
    file.save(os.path.join(upload_folder, unique_filename))

    # Parsear fecha si se envía
    publish_date = None
    raw_date = request.form.get("publish_date")
    if raw_date:
        try:
            publish_date = datetime.fromisoformat(raw_date).replace(tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Use ISO 8601 (ej: 2024-01-15)."}), 400

    # Crear la publicación
    pub = Publication(
        title=title,
        type_id=request.form.get("type_id") or None,
        publish_date=publish_date,
        resource_url=unique_filename,
        keywords=request.form.getlist("keywords"),
    )

    # Asociar autores
    for author_id in request.form.getlist("author_ids"):
        author = db.session.get(Author, author_id)
        if author:
            pub.authors.append(author)

    db.session.add(pub)
    db.session.commit()
    return jsonify(pub.to_dict()), 201


@bp.route("/publications/<string:pub_id>", methods=["PUT"])
@require_auth
def update_publication(pub_id):
    """
    Actualiza una publicación existente.
    Acepta multipart/form-data para permitir reemplazar el PDF,
    o application/json si no se sube nuevo archivo.
    """
    pub = db.get_or_404(Publication, pub_id)

    # Soportar tanto JSON como form-data
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
        get_list = request.form.getlist
    else:
        data = request.get_json() or {}
        get_list = lambda k: data.get(k, [])  # noqa: E731

    if "title" in data:
        pub.title = data["title"]
    if "type_id" in data:
        pub.type_id = data["type_id"] or None
    if "publish_date" in data and data["publish_date"]:
        try:
            pub.publish_date = datetime.fromisoformat(data["publish_date"]).replace(tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido."}), 400
    if "keywords" in data or get_list("keywords"):
        pub.keywords = get_list("keywords") if get_list("keywords") else data.get("keywords", pub.keywords)

    # Reemplazar autores si se envían nuevos
    new_author_ids = get_list("author_ids")
    if new_author_ids:
        pub.authors = []
        for author_id in new_author_ids:
            author = db.session.get(Author, author_id)
            if author:
                pub.authors.append(author)

    # Reemplazar PDF si se sube uno nuevo
    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "" and allowed_file(file.filename):
            # Eliminar el archivo anterior
            if pub.resource_url:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], pub.resource_url)
                if os.path.exists(old_path):
                    os.remove(old_path)

            upload_folder = ensure_upload_folder()
            unique_filename = f"{uuid_lib.uuid4()}_{secure_filename(file.filename)}"
            file.save(os.path.join(upload_folder, unique_filename))
            pub.resource_url = unique_filename

    db.session.commit()
    return jsonify(pub.to_dict()), 200


@bp.route("/publications/<string:pub_id>", methods=["DELETE"])
@require_auth
def delete_publication(pub_id):
    """Elimina una publicación y su archivo PDF asociado."""
    pub = db.get_or_404(Publication, pub_id)

    # Eliminar el archivo físico
    if pub.resource_url:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], pub.resource_url)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(pub)
    db.session.commit()
    return jsonify({"message": "Publicación eliminada correctamente."}), 200


@bp.route("/publications/<string:pub_id>/file", methods=["GET"])
def download_publication_file(pub_id):
    """Descarga el PDF de una publicación."""
    pub = db.get_or_404(Publication, pub_id)
    if not pub.resource_url:
        return jsonify({"error": "Esta publicación no tiene archivo adjunto."}), 404

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        pub.resource_url,
        as_attachment=True,
        download_name=pub.resource_url.split("_", 1)[-1],  # Nombre original sin el UUID
    )
