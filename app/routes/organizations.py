from flask import jsonify, request
from app.models import db, Organization
from app.auth import require_auth
from app.routes import bp

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
@require_auth(roles=["admin"])
def create_organization():
    """Crea una nueva organización."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "El campo 'name' es requerido."}), 400

    org = Organization(
        name=data["name"],
        website=data.get("website"),
        country=data.get("country"),
        description=data.get("description")
    )
    db.session.add(org)
    db.session.commit()
    return jsonify(org.to_dict()), 201

@bp.route("/organizations/<string:org_id>", methods=["PUT"])
@require_auth(roles=["admin"])
def update_organization(org_id):
    """Actualiza los datos de una organización."""
    org = db.get_or_404(Organization, org_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Body vacío."}), 400

    if "name" in data and data["name"]:
        org.name = data["name"]
    if "website" in data:
        org.website = data["website"]
    if "country" in data:
        org.country = data["country"]
    if "description" in data:
        org.description = data["description"]

    db.session.commit()
    return jsonify(org.to_dict()), 200

@bp.route("/organizations/<string:org_id>", methods=["DELETE"])
@require_auth(roles=["admin"])
def delete_organization(org_id):
    """Elimina una organización."""
    org = db.get_or_404(Organization, org_id)
    db.session.delete(org)
    db.session.commit()
    return jsonify({"message": "Organización eliminada correctamente."}), 200
