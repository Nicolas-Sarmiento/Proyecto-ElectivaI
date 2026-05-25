import weaviate
import weaviate.classes.config as wvcc
from flask import current_app

def get_weaviate_client():
    """Conecta al cluster de Weaviate Cloud (WCD)."""
    
    # URL completa (ej. https://xxx.weaviate.network)
    weaviate_url = current_app.config.get('WEAVIATE_URL')
    
    # API KEY de tu cluster Weaviate
    weaviate_api_key = current_app.config.get('WEAVIATE_API_KEY')
    
    # API KEY para vectorizar el texto con Hugging Face
    huggingface_api_key = current_app.config.get('HUGGINGFACE_API_KEY')

    # Headers necesarios para que Weaviate envíe el texto a HuggingFace
    headers = {}
    if huggingface_api_key:
        headers["X-HuggingFace-Api-Key"] = huggingface_api_key

    return weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
        headers=headers
    )

def inicializar_weaviate(app):
    """Inicializa la colección Publication en Weaviate Cloud."""
    with app.app_context():
        # Verificamos si tenemos creedenciales mínimas antes de conectar
        if not app.config.get('WEAVIATE_URL') or not app.config.get('WEAVIATE_API_KEY'):
            print("Weaviate URL o API KEY ausentes en .env. Omitiendo inicialización.")
            return

        try:
            client = get_weaviate_client()
            
            if not client.collections.exists("Publication"):
                client.collections.create(
                    name="Publication",
                    description="Colección de publicaciones académicas",
                    # Cambiamos OpenAI por HuggingFace
                    vectorizer_config=wvcc.Configure.Vectorizer.text2vec_huggingface(),
                    properties=[
                        wvcc.Property(name="publication_id", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="title", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="resource_url", data_type=wvcc.DataType.TEXT),
                        wvcc.Property(name="keywords", data_type=wvcc.DataType.TEXT_ARRAY),
                    ]
                )
                print(" Colección 'Publication' creada en Weaviate Cloud.")
            else:
                print("Colección 'Publication' detectada en Weaviate Cloud.")
                
            client.close()
        except Exception as e:
            print(f" Error inicializando Weaviate Cloud: {e}")

def guardar_publicacion(publication_id, title, resource_url, keywords):
    """Guarda/Sincroniza una publicación hacia Weaviate Cloud."""
    try:
        client = get_weaviate_client()
        coleccion = client.collections.get("Publication")
        
        coleccion.data.insert({
            "publication_id": str(publication_id),
            "title": title,
            "resource_url": resource_url,
            "keywords": keywords
        })
        
        client.close()
    except Exception as e:
        print(f"Error sincronizando con Weaviate Cloud: {e}")

def buscar_publicaciones(query: str, limite: int = 5):
    """Realiza una Búsqueda Híbrida en Weaviate Cloud."""
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
        print(f"Error buscando en Weaviate Cloud: {e}")
        return []
