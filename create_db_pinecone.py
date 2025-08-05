import os
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from freshRequests import recuperarArtigos
from backend.embeddings import get_embedding

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

index_name = os.getenv("PINECONE_INDEX_NAME")

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
else:
    print(f"O índice {index_name} já existe")
    

index = pc.Index(index_name)
#index.delete(delete_all=True)


class RateLimiter:
    
    def __init__(self):
        self.start_time = time.time()
        self.counter = 0
        self.max_per_minute = 129
        
    def check_limit(self):
        elapsed = time.time() - self.start_time
        if elapsed > 60:  
            self.start_time = time.time()
            self.counter = 0
        return self.counter < self.max_per_minute
    
    def increment(self):
        self.counter += 1


def process_and_upsert_articles():
    artigos = recuperarArtigos()
    if not artigos:
        print("Nenhum artigo para processar. Encerrando.")
        return
    vectors = []
    limiter = RateLimiter()
    total_processed = 0
    
    print(f"Iniciando processamento de {len(artigos)} artigos...")
    
    for artigo in artigos:

        while not limiter.check_limit():
            sleep_time = 60 - (time.time() - limiter.start_time)
            print(f"Limite de tokens/minuto atingido. Aguardando {sleep_time:.1f} segundos...")
            time.sleep(sleep_time)
        try:
            if not artigo.get('description'):
                print(f"Artigo {artigo.get('id', 'ID Desconhecido')} pulado por não ter descrição.")
                continue
            embedding = get_embedding(artigo['description'])
            limiter.increment()
            metadata_pinecone = {
                "id": artigo['id'],
                "title": artigo['title'],
                "description": artigo['description'],
                "category": artigo['category'],
                "folder": artigo['folder'],
                "tags": artigo['tags']  
            }
            
            if 'tags' in metadata_pinecone:
                tags = metadata_pinecone.pop('tags', [])
                for i, tag in enumerate(tags):
                    metadata_pinecone[f'tag_{i}'] = tag

            vectors.append({
                'id': str(artigo['id']),
                'values': embedding,
                'metadata': metadata_pinecone
            })
            total_processed += 1
            if total_processed % 10 == 0:
                elapsed = time.time() - limiter.start_time
                rate = limiter.counter / max(1, elapsed) * 60
                print(f"Progresso: {total_processed}/{len(artigos)} | "
                      f"Taxa atual: {rate:.1f} embeddings/min | "
                      f"Total tokens: {limiter.counter * 1536}/200.000 por minuto")
        except Exception as e:
            print(f"Erro inesperado ao processar o artigo {artigo.get('id', 'ID Desconhecido')}: {str(e)}") 
            continue

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"Upsert concluído para lote {i//batch_size + 1}/{(len(vectors)//batch_size)+1}")
        except Exception as e:
            print(f"Erro no upsert do lote {i//batch_size + 1}: {str(e)}")
    
    print(f"Processo finalizado. Artigos processados: {total_processed}")
    print(f"Total embeddings gerados: {len(vectors)}")
    print(f"Total tokens consumidos: {total_processed * 1536}")

if __name__ == "__main__":
    process_and_upsert_articles()