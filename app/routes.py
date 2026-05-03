from flask import Blueprint, jsonify, request

from app.models import Organization, PublicationType, db

bp = Blueprint("main", __name__)


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
def delete_publication_type(type_id):
    """Elimina un tipo de publicación."""
    pub_type = db.get_or_404(PublicationType, type_id)
    db.session.delete(pub_type)
    db.session.commit()
    return jsonify({"message": "Tipo de publicación eliminado correctamente."}), 200
