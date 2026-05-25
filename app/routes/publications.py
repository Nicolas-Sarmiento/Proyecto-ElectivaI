import os
import uuid as uuid_lib
from datetime import datetime, timezone
import re

from flask import current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from app.models import db, Publication, PublicationType, Author
from app.auth import require_auth
from app.routes import bp
from app.routes.utils import allowed_file, ensure_upload_folder

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
@require_auth(roles=["admin"])
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
@require_auth(roles=["admin"])
def delete_publication_type(type_id):
    """Elimina un tipo de publicación."""
    pub_type = db.get_or_404(PublicationType, type_id)
    db.session.delete(pub_type)
    db.session.commit()
    return jsonify({"message": "Tipo de publicación eliminado correctamente."}), 200

@bp.route("/publications", methods=["GET"])
def list_publications():
    """
    Lista todas las publicaciones.
    Query params opcionales:
        keyword (str): Filtra publicaciones que contengan esta palabra clave.
        author_id (str): Filtra publicaciones por un autor en específico.
    """
    keywords = request.args.getlist("keyword")
    author_id = request.args.get("author_id")
    
    query = Publication.query

    if keywords:
        or_conditions = []
        for kw_raw in keywords:
            if not kw_raw.strip():
                continue
            words = [w.strip() for w in re.split(r'[, ]+', kw_raw) if w.strip()]
            for word in words:
                or_conditions.append(
                    db.cast(Publication.keywords, db.String).ilike(f"%{word}%")
                )
        if or_conditions:
            query = query.filter(or_(*or_conditions))

    if author_id:
        query = query.filter(Publication.authors.any(author_id=author_id))

    publications = query.order_by(Publication.title).all()
    return jsonify([p.to_dict() for p in publications]), 200

@bp.route("/publications/<string:pub_id>", methods=["GET"])
def get_publication(pub_id):
    """Obtiene una publicación por ID."""
    pub = db.get_or_404(Publication, pub_id)
    return jsonify(pub.to_dict()), 200

@bp.route("/publications", methods=["POST"])
@require_auth(roles=["admin"])
def create_publication():
    """
    Crea una nueva publicación con un archivo PDF adjunto.
    """
    title = request.form.get("title")
    if not title:
        return jsonify({"error": "El campo 'title' es requerido."}), 400

    if "file" not in request.files:
        return jsonify({"error": "Se requiere un archivo PDF (campo 'file')."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Solo se permiten archivos PDF."}), 400

    upload_folder = ensure_upload_folder()
    original_name = secure_filename(file.filename)
    unique_filename = f"{uuid_lib.uuid4()}_{original_name}"
    pdf_path = os.path.join(upload_folder, unique_filename)
    file.save(pdf_path)

    publish_date = None
    raw_date = request.form.get("publish_date")
    if raw_date:
        try:
            publish_date = datetime.fromisoformat(raw_date).replace(tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Use ISO 8601 (ej: 2024-01-15)."}), 400

    pub = Publication(
        title=title,
        type_id=request.form.get("type_id") or None,
        publish_date=publish_date,
        resource_url=unique_filename,
        keywords=request.form.getlist("keywords"),
    )

    for author_id in request.form.getlist("author_ids"):
        author = db.session.get(Author, author_id)
        if author:
            pub.authors.append(author)

    db.session.add(pub)
    db.session.commit()

    try:
        from app.embeddings import process_pdf_for_publication
        chunks_count = process_pdf_for_publication(pub.publication_id, pdf_path)
        current_app.logger.info("Publicación '%s' creada con %d chunks indexados.", title, chunks_count)
    except Exception as e:
        current_app.logger.error("Error generando embeddings: %s", e)

    return jsonify(pub.to_dict()), 201

@bp.route("/publications/<string:pub_id>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_publication(pub_id):
    """
    Actualiza una publicación existente.
    """
    pub = db.get_or_404(Publication, pub_id)

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

    new_author_ids = get_list("author_ids")
    if new_author_ids:
        pub.authors = []
        for author_id in new_author_ids:
            author = db.session.get(Author, author_id)
            if author:
                pub.authors.append(author)

    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "" and allowed_file(file.filename):
            if pub.resource_url:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], pub.resource_url)
                if os.path.exists(old_path):
                    os.remove(old_path)

            upload_folder = ensure_upload_folder()
            unique_filename = f"{uuid_lib.uuid4()}_{secure_filename(file.filename)}"
            pdf_path = os.path.join(upload_folder, unique_filename)
            file.save(pdf_path)
            pub.resource_url = unique_filename

            try:
                from app.embeddings import delete_chunks_for_publication, process_pdf_for_publication
                delete_chunks_for_publication(pub.publication_id)
                process_pdf_for_publication(pub.publication_id, pdf_path)
            except Exception as e:
                current_app.logger.error("Error regenerando embeddings: %s", e)

    db.session.commit()
    return jsonify(pub.to_dict()), 200

@bp.route("/publications/<string:pub_id>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_publication(pub_id):
    """Elimina una publicación y su archivo PDF asociado."""
    pub = db.get_or_404(Publication, pub_id)

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
        download_name=pub.resource_url.split("_", 1)[-1],
    )
