import os
import re
import math
import argparse
from datetime import timezone
from app import create_app
from app.models import db, Publication, Author, PublicationType
from app.embeddings import semantic_search
from populate_db import populate_from_arxiv

app = create_app()

# Definición de Queries de Prueba y sus reglas de relevancia heurísticas
TEST_QUERIES = [
    {
        "query": "neural networks for computer vision and image classification",
        "keywords": ["vision", "image", "classification", "cnn", "convolutional", "object", "detection", "cs.CV"],
        "category": "computer_vision"
    },
    {
        "query": "natural language processing and transformer models",
        "keywords": ["language", "nlp", "text", "transformer", "bert", "gpt", "translation", "cs.CL", "attention"],
        "category": "nlp"
    },
    {
        "query": "optimization algorithms and gradient descent",
        "keywords": ["optimization", "gradient", "descent", "sgd", "optimizer", "convex", "cs.LG", "stat.ML"],
        "category": "optimization"
    }
]

def get_ground_truth(publications):
    """
    Genera el diccionario de ground truth (relevancia) para cada query
    basado en las palabras clave y categorías de cada publicación.
    """
    ground_truth = {}
    for q_data in TEST_QUERIES:
        query = q_data["query"]
        ground_truth[query] = set()
        
        for pub in publications:
            # Unir título, keywords y categorías para buscar coincidencia
            text_to_check = (pub.title + " " + " ".join(pub.keywords)).lower()
            
            # Si contiene alguna de las palabras clave de la query, es relevante
            is_rel = False
            for kw in q_data["keywords"]:
                if kw.lower() in text_to_check:
                    is_rel = True
                    break
            
            if is_rel:
                ground_truth[query].add(pub.publication_id)
                
    return ground_truth

def run_keyword_search(query_text):
    """
    Simula la búsqueda por palabras clave tal como está implementada en list_publications
    """
    from sqlalchemy import or_
    words = [w.strip() for w in re.split(r'[, ]+', query_text) if w.strip()]
    if not words:
        return []
        
    or_conditions = []
    for word in words:
        or_conditions.append(
            db.cast(Publication.keywords, db.String).ilike(f"%{word}%")
        )
        
    query = Publication.query.filter(or_(*or_conditions))
    publications = query.order_by(Publication.title).all()
    return [p.to_dict() for p in publications]

def run_semantic_search(query_text, limit=5):
    """
    Ejecuta la búsqueda semántica real usando embeddings
    """
    return semantic_search(query_text, limit=limit)

# --- Cálculo de Métricas ---

def calculate_precision_recall(results, relevant_ids, k=5):
    top_k_results = results[:k]
    if not top_k_results:
        return 0.0, 0.0
        
    retrieved_relevant = sum(1 for r in top_k_results if uuid.UUID(r["publication_id"]) in relevant_ids)
    
    precision = retrieved_relevant / min(k, len(top_k_results))
    recall = retrieved_relevant / len(relevant_ids) if len(relevant_ids) > 0 else 0.0
    
    return precision, recall

def calculate_mrr(results, relevant_ids):
    for idx, r in enumerate(results):
        if uuid.UUID(r["publication_id"]) in relevant_ids:
            return 1.0 / (idx + 1)
    return 0.0

def calculate_ndcg(results, relevant_ids, k=5):
    top_k_results = results[:k]
    dcg = 0.0
    for idx, r in enumerate(top_k_results):
        if uuid.UUID(r["publication_id"]) in relevant_ids:
            # Relevancia binaria (1 si es relevante, 0 si no)
            dcg += 1.0 / math.log2(idx + 2)
            
    # Calcular IDCG (Ideal DCG)
    idcg = 0.0
    num_relevant = min(k, len(relevant_ids))
    for idx in range(num_relevant):
        idcg += 1.0 / math.log2(idx + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg

import uuid

def evaluate():
    with app.app_context():
        publications = Publication.query.all()
        
        # Si no hay suficientes publicaciones, poblamos automáticamente
        if len(publications) < 10:
            print(f"Base de datos casi vacía ({len(publications)} publicaciones).")
            print("Poblando automáticamente con papers de ArXiv para la evaluación...")
            
            # Descargamos 4 papers de cada categoría para tener variedad
            populate_from_arxiv(query="computer vision", max_results=4)
            populate_from_arxiv(query="natural language processing", max_results=4)
            populate_from_arxiv(query="machine learning optimization", max_results=4)
            
            # Recargar
            publications = Publication.query.all()
            
        print(f"\nEvaluando con {len(publications)} publicaciones en base de datos.")
        
        ground_truth = get_ground_truth(publications)
        
        # Estructuras para acumular métricas
        kw_metrics = {"precision": 0.0, "recall": 0.0, "mrr": 0.0, "ndcg": 0.0}
        sem_metrics = {"precision": 0.0, "recall": 0.0, "mrr": 0.0, "ndcg": 0.0}
        
        num_queries = len(TEST_QUERIES)
        
        print("\n" + "="*80)
        print(f"{'QUERY EVALUADA':<50} | {'KW REL':<6} | {'SEM REL':<6}")
        print("="*80)
        
        for q_data in TEST_QUERIES:
            query = q_data["query"]
            relevant_ids = ground_truth[query]
            
            if not relevant_ids:
                print(f"Advertencia: No hay documentos relevantes para la query '{query}'. Saltando...")
                num_queries -= 1
                continue
                
            # Ejecutar búsquedas
            kw_results = run_keyword_search(query)
            sem_results = run_semantic_search(query, limit=5)
            
            # Calcular métricas individuales
            kw_p, kw_r = calculate_precision_recall(kw_results, relevant_ids, k=5)
            kw_mrr = calculate_mrr(kw_results, relevant_ids)
            kw_ndcg = calculate_ndcg(kw_results, relevant_ids, k=5)
            
            sem_p, sem_r = calculate_precision_recall(sem_results, relevant_ids, k=5)
            sem_mrr = calculate_mrr(sem_results, relevant_ids)
            sem_ndcg = calculate_ndcg(sem_results, relevant_ids, k=5)
            
            # Acumular
            kw_metrics["precision"] += kw_p
            kw_metrics["recall"] += kw_r
            kw_metrics["mrr"] += kw_mrr
            kw_metrics["ndcg"] += kw_ndcg
            
            sem_metrics["precision"] += sem_p
            sem_metrics["recall"] += sem_r
            sem_metrics["mrr"] += sem_mrr
            sem_metrics["ndcg"] += sem_ndcg
            
            # Mostrar resultados individuales de relevancia
            kw_ret_rel = sum(1 for r in kw_results[:5] if uuid.UUID(r["publication_id"]) in relevant_ids)
            sem_ret_rel = sum(1 for r in sem_results[:5] if uuid.UUID(r["publication_id"]) in relevant_ids)
            
            short_query = query[:47] + "..." if len(query) > 50 else query
            print(f"{short_query:<50} | {kw_ret_rel}/{len(relevant_ids):<4} | {sem_ret_rel}/{len(relevant_ids):<4}")
            
        if num_queries == 0:
            print("No se pudieron evaluar queries debido a falta de datos relevantes.")
            return
            
        # Promediar métricas
        for key in kw_metrics:
            kw_metrics[key] /= num_queries
            sem_metrics[key] /= num_queries
            
        print("\n" + "="*50)
        print(f"{'MÉTRICA (k=5)':<20} | {'KEYWORD SEARCH':<14} | {'SEMANTIC SEARCH':<15}")
        print("="*50)
        print(f"{'Precision@5':<20} | {kw_metrics['precision']:<14.4f} | {sem_metrics['precision']:<15.4f}")
        print(f"{'Recall@5':<20} | {kw_metrics['recall']:<14.4f} | {sem_metrics['recall']:<15.4f}")
        print(f"{'MRR':<20} | {kw_metrics['mrr']:<14.4f} | {sem_metrics['mrr']:<15.4f}")
        print(f"{'NDCG@5':<20} | {kw_metrics['ndcg']:<14.4f} | {sem_metrics['ndcg']:<15.4f}")
        print("="*50)
        
        print("\nInterpretación:")
        print("- Precision@5: Porcentaje de resultados correctos en el top 5.")
        print("- Recall@5: Qué fracción del total de documentos relevantes se recuperó.")
        print("- MRR: Cuán rápido apareció el primer resultado correcto (1.00 es el primer lugar).")
        print("- NDCG@5: Calidad del ranking considerando la posición de los aciertos.")

if __name__ == "__main__":
    evaluate()
