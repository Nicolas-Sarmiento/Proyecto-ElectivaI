import weaviate
import weaviate.classes.config as wvcc
from flask import current_app

def get_weaviate_client():
    """Conecta al cliente de Weaviate usando la configuración de Flask."""
    host = current_app.config.get('WEAVIATE_HOST', 'localhost')
    port = current_app.config.get('WEAVIATE_PORT', 8080)
    grpc_port = current_app.config.get('WEAVIATE_GRPC_PORT', 50051)
    
    return weaviate.connect_to_local(
        host=host,
        port=port,
        grpc_port=grpc_port
    )

def inicializar_weaviate(app):
    """Inicializa la colección Publication en Weaviate."""
    with app.app_context():
        try:
            client = get_weaviate_client()
            
            if not client.collections.exists("Publication"):
                client.collections.create(
                    name="Publication",
                    description="Colección de publicaciones académicas",
                    vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
                    properties=[
                        wvcc.Property(name="publication_id", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="title", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="resource_url", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="keywords", data_type=wvcc.DataType.TEXT_ARRAY),
                    ]
                )
                print("Colección 'Publication' creada en Weaviate.")
            else:
                print("Colección 'Publication' ya existe en Weaviate.")
                
            client.close()
        except Exception as e:
            print(f"Error inicializando Weaviate: {e}")

def guardar_publicacion(publication_id, title, resource_url, keywords):
    """Guarda/Sincroniza una publicación hacia Weaviate."""
    try:
        client = get_weaviate_client()
        coleccion = client.collections.get("Publication")
        
        # En Weaviate generamos el uuid o usamos insert
        coleccion.data.insert({
            "publication_id": str(publication_id),
            "title": title,
            "resource_url": resource_url,
            "keywords": keywords
        })
        
        client.close()
    except Exception as e:
        print(f"Error sincronizando con Weaviate: {e}")

def buscar_publicaciones(query: str, limite: int = 5):
    """Realiza una Búsqueda Híbrida en las publicaciones."""
    try:
        client = get_weaviate_client()
        coleccion = client.collections.get("Publication")
        
        response = coleccion.query.hybrid(
            query=query,
            limit=limite,
            alpha=0.5 # 50% semántico, 50% BM25
        )
        
        resultados = []
        for item in response.objects:
            resultados.append({
                "publication_id": item.properties["publication_id"],
                "title": item.properties["title"],
                "resource_url": item.properties.get("resource_url", ""),
                "keywords": item.properties.get("keywords", [])
            })
            
        client.close()
        return resultados
    except Exception as e:
        print(f"Error buscando en Weaviate: {e}")
        return []
