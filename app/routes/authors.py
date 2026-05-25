from flask import jsonify, request
from app.models import db, Author
from app.auth import require_auth
from app.routes import bp

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
@require_auth(roles=["admin"])
def create_author():
    """
    Crea un nuevo autor.
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
@require_auth(roles=["admin"])
def update_author(author_id):
    """
    Actualiza los datos de un autor.
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
@require_auth(roles=["admin"])
def delete_author(author_id):
    """Elimina un autor."""
    author = db.get_or_404(Author, author_id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "Autor eliminado correctamente."}), 200
