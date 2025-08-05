# Atendente N2 Virtual

Um agente de IA que atua como um atendente de suporte virtual (Nível 2), otimizado para fornecer respostas rápidas e precisas com base em uma base de conhecimento pré-existente.

## 📖 Sobre o Projeto

Este projeto foi desenvolvido para ser um bot de auxílio a atendentes de suporte, agilizando a localização de informações em bases de conhecimento muito extensas. Ele funciona da seguinte maneira:

1.  Um atendente humano envia uma pergunta para um bot no Discord.
2.  O bot recebe a pergunta e a utiliza para consultar uma base de dados vetorizada (Pinecone) que contém toda a base de conhecimento.
3.  A consulta retorna os documentos mais relevantes, que são enviados a uma LLM (Modelo de Linguagem Grande) da OpenAI.
4.  A LLM gera uma resposta coesa e contextualizada com base nos documentos.
5.  A resposta final é enviada de volta para o atendente no canal do Discord.

## ✨ Funcionalidades Principais

-   **Extração de Dados:** Extrai e processa a base de conhecimento a partir de uma fonte externa (via requisições).
-   **Vetorização:** Converte os documentos da base de conhecimento em vetores e os armazena em um banco de dados otimizado para buscas de similaridade (Pinecone).
-   **Integração com Discord:** Um bot totalmente funcional que recebe e responde a mensagens de usuários em um servidor do Discord.
-   **Processamento de Linguagem Natural:** Utiliza uma LLM para interpretar as perguntas dos usuários e gerar respostas precisas com base nos dados encontrados.

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3.13.5
-   **Orquestração de LLM:** LangChain
-   **Banco de Dados Vetorizado:** Pinecone
-   **LLM e Embeddings:** OpenAI
-   **Servidor API:** FastAPI
-   **Servidor ASGI:** Uvicorn
-   **Bot do Discord:** Discord.py

## 📁 Estrutura do Projeto

A estrutura de pastas e arquivos principais do projeto é a seguinte:

├── backend/
│   ├── pycache/
│   ├── init.py         # Inicializador do módulo backend
│   ├── bot.py              # Lógica principal do bot do Discord
│   ├── embeddings.py       # Funções para gerar embeddings
│   ├── main.py             # Arquivo principal da API com FastAPI
│   ├── query_processor.py  # Processador de consultas na base vetorizada
│   └── schemas.py          # Schemas Pydantic para a API
├── chroma_db/              # (Opcional) Diretório para banco local ChromaDB
├── venv/                   # Ambiente virtual do Python
├── .env                    # Arquivo para variáveis de ambiente (NÃO versionar)
├── .gitignore              # Arquivos e pastas ignorados pelo Git
├── create_db_pinecone.py   # Script para criar e popular o DB no Pinecone
├── freshRequests.py        # Script para fazer requisições à base de conhecimento
├── requirements.txt        # Lista de dependências do projeto
└── run.py                  # (Opcional) Script para iniciar a aplicação

## 🚀 Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.13 ou superior instalado.
-   Git instalado.

### 2. Clonar o Repositório

git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA_DO_PROJETO>

### 3. Configurar Ambiente Virtual e Dependências
Crie e ative um ambiente virtual:

# Para Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate

Instale as dependências necessárias:

pip install -r requirements.txt

### 4. Configurar Variáveis de Ambiente

Crie um arquivo .env na raiz do projeto e adicione as variáveis de ambiente necessárias:

OPENAI_API_KEY=seu_chave_api_openai
DISCORD_TOKEN=seu_token_do_discord
PINECONE_API_KEY=seu_chave_api_pinecone
PINECONE_ENVIRONMENT=seu_ambiente_pinecone
PINECONE_INDEX_NAME=seu_nome_do_indice_pinecone
FRESHDESK_API_KEY=seu_chave_api_freshdesk
FRESHDESK_DOMAIN=seu_dominio_freshdesk

## ▶️ Como Usar
Para colocar o sistema em funcionamento, você precisa executar os scripts na ordem correta.

### 1. Popular o Banco de Dados (Executar apenas uma vez)
Primeiro, execute o script para extrair os dados e popular seu banco de dados vetorizado no Pinecone.

python freshRequests.py

### 2. Iniciar o Servidor da API
Em um terminal, inicie o servidor local que gerencia as requisições do backend.

uvicorn backend.main:app --reload


### 3. Iniciar o Bot do Discord
Em outro terminal, com o ambiente virtual ativado, inicie o bot que irá interagir no Discord.

python bot.py

Após esses passos, o bot deverá estar online no seu servidor do Discord e pronto para responder às perguntas.
