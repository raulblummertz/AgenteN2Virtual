import requests
import os
from dotenv import load_dotenv
from langchain.schema import Document
import sys
print("Python executable:", sys.executable)


load_dotenv()
api_key = os.getenv("FRESHDESK_API_KEY")
domain = os.getenv("FRESHDESK_DOMAIN")
def recuperarArtigos():
    responseCategories = requests.get(f"https://{domain}/api/v2/solutions/categories", auth=(api_key, "X"))
    listaCategoria = {}
    listaPasta = {}
    listaArtigo = []

    if responseCategories.status_code == 200:
        for categories in responseCategories.json():
           # dadosCategoria = { "id": categories['id'], "name": categories['name'] }
           #listaCategoria.append(dadosCategoria)
           listaCategoria[categories['id']] = categories.get('name', 'Categoria sem nome')

 
        for cat in listaCategoria.keys():
            responseFolders = requests.get(f"https://{domain}/api/v2/solutions/categories/{cat}/folders", auth=(api_key, "X"))
            if responseFolders.status_code == 200:
                for folders in responseFolders.json():
                    #dadosFolder = { "id": folders['id'], "name": folders['name'] }
                    #listaPasta.append(dadosFolder)
                    listaPasta[folders['id']] = {
                        "name": folders.get('name', 'Pasta sem nome'),
                        "category_name": listaCategoria[cat]
                    } 

        for folder_id, folder_data in listaPasta.items():
            responseArticles = requests.get(f"https://{domain}/api/v2/solutions/folders/{folder_id}/articles", auth=(api_key, "X"))
            if responseArticles.status_code == 200:
               for article in responseArticles.json():
                
            
                raw_text = article.get('description_text', '')

                clean_text = raw_text.strip()
                dadosArtigo = {
                    "id": article.get('id'),
                    "title": article.get('title', 'Artigo Sem Título'),
                    "description": clean_text, 
                    "tags": article.get('tags', []),
                    "folder": folder_data['name'],
                    "category": folder_data['category_name']
                }

                if not dadosArtigo['id']:
                    print(f"AVISO: Artigo encontrado sem ID na pasta '{folder_data['name']}'. Pulando.")
                    continue
                listaArtigo.append(dadosArtigo)
    return listaArtigo
    #return []


def criar_documentos(artigos):
    return [
    Document (page_content=artigo['description'], metadata=artigo['metadata']) for artigo in artigos
    ]

