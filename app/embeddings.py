"""
Módulo de embeddings: extracción de PDF, chunking con overlap,
generación de embeddings con sentence-transformers y búsqueda semántica con pgvector.
"""

import logging
from typing import Optional

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from flask import current_app

logger = logging.getLogger(__name__)

# Singleton del modelo — se carga una sola vez (lazy)
_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    """Carga el modelo de embeddings (lazy singleton)."""
    global _model
    if _model is None:
        model_name = current_app.config.get(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        logger.info("Cargando modelo de embeddings: %s", model_name)
        _model = SentenceTransformer(model_name)
        logger.info("Modelo cargado correctamente.")
    return _model


# ─── Extracción de texto del PDF ──────────────────────────────────────────────


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extrae el texto de cada página de un PDF.
    Retorna una lista de dicts con page_number y text.
    """
    pages = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            # Eliminar caracteres NUL para evitar errores en PostgreSQL
            cleaned_text = text.replace("\x00", "").strip()
            if cleaned_text:
                pages.append({
                    "page_number": page_num + 1,
                    "text": cleaned_text,
                })
    doc.close()
    return pages


# ─── Chunking con overlap ────────────────────────────────────────────────────


def create_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Divide un texto en fragmentos (chunks) con solapamiento.
    Intenta cortar en espacios para no partir palabras.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Si no es el último chunk, busca un espacio cercano para cortar limpio
        if end < len(text):
            space_idx = text.rfind(" ", start + chunk_size // 2, end)
            if space_idx != -1:
                end = space_idx

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Avanza con overlap
        start = end - overlap if end - overlap > start else end

    return chunks


# ─── Generación de embeddings ─────────────────────────────────────────────────


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos usando el modelo local."""
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


# ─── Procesamiento completo de un PDF ─────────────────────────────────────────


def process_pdf_for_publication(publication_id, pdf_path: str) -> int:
    """
    Pipeline completo: extraer texto del PDF → crear chunks con overlap
    → generar embeddings → almacenar en la tabla document_chunks (pgvector).

    Retorna la cantidad de chunks procesados.
    """
    from app.models import DocumentChunk, db

    chunk_size = current_app.config.get("CHUNK_SIZE", 500)
    chunk_overlap = current_app.config.get("CHUNK_OVERLAP", 100)

    # 1. Extraer texto por página
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        logger.warning("No se pudo extraer texto del PDF: %s", pdf_path)
        return 0

    # 2. Crear chunks con overlap para cada página
    all_chunks = []
    for page_data in pages:
        page_chunks = create_chunks(page_data["text"], chunk_size, chunk_overlap)
        for idx, chunk_text in enumerate(page_chunks):
            all_chunks.append({
                "page_number": page_data["page_number"],
                "chunk_index": idx,
                "text_content": chunk_text,
            })

    if not all_chunks:
        return 0

    # 3. Generar embeddings para todos los chunks de una vez
    texts = [c["text_content"] for c in all_chunks]
    logger.info(
        "Generando embeddings para %d chunks de la publicación %s",
        len(texts), publication_id
    )
    embeddings = generate_embeddings(texts)

    # 4. Almacenar en pgvector
    for chunk_data, embedding in zip(all_chunks, embeddings):
        chunk = DocumentChunk(
            publication_id=publication_id,
            page_number=chunk_data["page_number"],
            chunk_index=chunk_data["chunk_index"],
            text_content=chunk_data["text_content"],
            embedding=embedding,
        )
        db.session.add(chunk)

    db.session.commit()
    logger.info("Almacenados %d chunks para publicación %s", len(all_chunks), publication_id)
    return len(all_chunks)


# ─── Eliminar chunks de una publicación ───────────────────────────────────────


def delete_chunks_for_publication(publication_id) -> int:
    """Elimina todos los chunks de una publicación. Retorna la cantidad eliminada."""
    from app.models import DocumentChunk, db

    deleted = DocumentChunk.query.filter_by(publication_id=publication_id).delete()
    db.session.commit()
    return deleted


# ─── Búsqueda semántica ──────────────────────────────────────────────────────


def semantic_search(query: str, limit: int = 10) -> list[dict]:
    """
    Búsqueda por lenguaje natural usando similitud coseno en pgvector.
    Agrupa resultados por publicación y retorna los más relevantes.
    """
    from app.models import DocumentChunk, Publication, db

    # Generar embedding del query
    query_embedding = generate_embeddings([query])[0]

    # Buscar chunks más cercanos usando distancia coseno
    results = (
        db.session.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .order_by("distance")
        .limit(limit * 3)  # Traer más para agrupar por publicación
        .all()
    )

    # Agrupar por publicación, mantener el mejor match
    seen_publications: dict[str, dict] = {}
    for chunk, distance in results:
        pub_id = str(chunk.publication_id)
        similarity = round(1 - distance, 4)

        if pub_id not in seen_publications or similarity > seen_publications[pub_id]["similarity"]:
            seen_publications[pub_id] = {
                "publication_id": pub_id,
                "similarity": similarity,
                "matched_text": chunk.text_content,
                "matched_page": chunk.page_number,
            }

    # Ordenar por similitud descendente y limitar
    sorted_results = sorted(
        seen_publications.values(),
        key=lambda x: x["similarity"],
        reverse=True,
    )[:limit]

    # Enriquecer con datos completos de la publicación
    final_results = []
    for result in sorted_results:
        pub = db.session.get(Publication, result["publication_id"])
        if pub:
            pub_dict = pub.to_dict()
            pub_dict["similarity"] = result["similarity"]
            pub_dict["matched_text"] = result["matched_text"]
            pub_dict["matched_page"] = result["matched_page"]
            final_results.append(pub_dict)

    return final_results
