from flask import jsonify, request, current_app
from app.routes import bp

@bp.route("/search", methods=["GET"])
def search_publications():
    """
    Búsqueda por lenguaje natural usando embeddings y pgvector.
    Query params:
        q     (str, requerido): Consulta en lenguaje natural.
        limit (int, opcional):  Número máximo de resultados (default 10).
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "El parámetro 'q' es requerido."}), 400

    limit = request.args.get("limit", 10, type=int)

    try:
        from app.embeddings import semantic_search
        results = semantic_search(query, limit=limit)
        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error("Error en búsqueda semántica: %s", e)
        return jsonify({"error": "Error al realizar la búsqueda semántica."}), 500
