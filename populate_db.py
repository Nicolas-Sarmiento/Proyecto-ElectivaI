import os
import uuid
import requests
import argparse
from datetime import timezone

try:
    import arxiv
except ImportError:
    print("Por favor instala arxiv: pip install arxiv")
    exit(1)

from app import create_app
from app.models import db, Publication, Author, PublicationType
from app.routes.utils import ensure_upload_folder
from app.embeddings import process_pdf_for_publication

app = create_app()

def download_pdf(url, output_path):
    print(f"Descargando PDF desde {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def populate_from_arxiv(query="machine learning", max_results=10):
    with app.app_context():
        # Crear un tipo de publicación base
        pub_type = PublicationType.query.filter_by(type_name="Paper").first()
        if not pub_type:
            pub_type = PublicationType(type_name="Paper")
            db.session.add(pub_type)
            db.session.commit()

        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        upload_folder = ensure_upload_folder()

        for result in client.results(search):
            print(f"\n--- Procesando: {result.title} ---")
            
            # 1. Crear Autores
            author_objs = []
            for author in result.authors:
                names = author.name.split()
                first_name = names[0]
                last_name = " ".join(names[1:]) if len(names) > 1 else ""
                
                a = Author.query.filter_by(first_name=first_name, last_name=last_name).first()
                if not a:
                    a = Author(first_name=first_name, last_name=last_name)
                    db.session.add(a)
                    db.session.commit()
                author_objs.append(a)

            # 2. Descargar PDF
            unique_filename = f"{uuid.uuid4()}_arxiv_paper.pdf"
            pdf_path = os.path.join(upload_folder, unique_filename)
            
            if download_pdf(result.pdf_url, pdf_path):
                # 3. Crear Publicación en BD
                pub = Publication(
                    title=result.title,
                    type_id=pub_type.type_id,
                    publish_date=result.published.replace(tzinfo=timezone.utc) if result.published else None,
                    resource_url=unique_filename,
                    keywords=[query, "arxiv"] + [cat for cat in result.categories]
                )
                
                for a in author_objs:
                    pub.authors.append(a)
                    
                db.session.add(pub)
                db.session.commit()
                
                # 4. Generar Embeddings
                print("Generando embeddings (esto puede tardar)...")
                try:
                    chunks_count = process_pdf_for_publication(pub.publication_id, pdf_path)
                    print(f"Éxito! Creados {chunks_count} chunks para '{result.title}'")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error generando embeddings: {e}")
            else:
                print("Error descargando el PDF.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poblar BD con papers de ArXiv")
    parser.add_argument("--query", type=str, default="machine learning", help="Término de búsqueda en ArXiv")
    parser.add_argument("--max", type=int, default=5, help="Número de papers a descargar")
    
    args = parser.parse_args()
    populate_from_arxiv(query=args.query, max_results=args.max)
