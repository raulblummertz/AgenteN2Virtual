import os
import logging
from typing import List, Optional, Dict, Any
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment=os.environ.get("PINECONE_ENVIRONMENT")
)
index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))

class QueryProcessor:
    def __init__(self):
        pass

    def get_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def generate_response(self, query: str) -> str:
        logging.info(f"Recebida nova consulta do usuário: '{query}'")
        palavras_chave = self._extrair_palavras_chave(query)
        filtro = self._construir_filtro(palavras_chave)
        logging.info(f"Filtro gerado para a busca no Pinecone: {filtro}")

        
        query_embedding = self.get_embedding(query)
        logging.info("Realizando busca por similaridade no Pinecone...")
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            filter=filtro
        )
        if not results.matches:
            logging.warning(f"Nenhum resultado encontrado no Pinecone para a consulta: '{query}'")
            return "Não encontrei informações relevantes para responder à sua pergunta nos materiais disponíveis."

        logging.info(f"Encontrados {len(results.matches)} artigos relevantes no Pinecone.")
        logging.debug(f"IDs dos artigos encontrados: {[match.id for match in results.matches]}")
        logging.debug(f"Scores de similaridade: {[match.score for match in results.matches]}")
            
        context = "\n\n".join(
            [match.metadata['description'] for match in results.matches]
        )
        logging.info(f"Contexto de {len(context)} caracteres gerado para a OpenAI.")
        logging.debug(f"Contexto completo enviado para a OpenAI:\n---\n{context}\n---")

        if not context:
            logging.error("Falha ao construir o contexto a partir dos resultados do Pinecone.")
            return "Ocorreu um erro ao processar sua solicitação. Não foi possível gerar um contexto."

        logging.info("Enviando requisição final para a API da OpenAI...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        Você é um assistente virtual altamente especializado em SUPORTE TÉCNICO da empresa Next Fit.

                        Sua missão é responder perguntas com BASE EXCLUSIVA nos artigos abaixo:
                        {context}

                        INSTRUÇÕES IMPORTANTES:
                        1. Responda somente se a informação estiver claramente presente nos artigos.
                        2. Se a resposta não estiver nos artigos, diga: "Não encontrei essa informação nos materiais disponíveis."
                        3. Seja técnico, direto e evite rodeios.
                        4. Responda em formato de lista ou passos, se aplicável.
                        5. Use termos e instruções claras, como se estivesse explicando a um colega de suporte experiente.
                        6. Nunca invente ou assuma informações além do conteúdo fornecido.
                        7. A resposta deve ter menos 2000 caracteres, para respeitar os limites do discord.
                        """.replace("{context}", context)
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                    ],
                temperature=0
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Erro ao processar a requisição para a API da OpenAI: {str(e)}")
            return "Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde."

    def _extrair_palavras_chave(self, query: str) -> List[str]:
        palavras = query.lower().split()
        return [palavra for palavra in palavras if len(palavra) >= 3]

    def _construir_filtro(self, palavras_candidatas: List[str]) -> Optional[Dict[str, Any]]:
        if not palavras_candidatas:
            return None
        
        conditions = []
        for palavra in palavras_candidatas:
            tag_conditions = [
                {f"tag_{i}": {"$eq": palavra}} for i in range(10)
            ]
            conditions.extend(tag_conditions)
        
        return {"$or": conditions}