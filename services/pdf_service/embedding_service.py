# embedding_service.py

import os
import json
import openai
from .pdf_loader import load_and_process_pdfs
from config.logging_config import logger

# Configurando o cliente para usar o LLMStudio
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"

EMBEDDINGS_DIRECTORY = "data/embeddings/"

def generate_embedding(text, model="nomic-ai/nomic-embed-text-v1.5"):
    logger.info(f"Gerando embedding para o texto: {text[:60]}...")
    text = text.replace("\n", " ")

    try:
        # Chamando o endpoint de embeddings da API diretamente
        response = openai.Embedding.create(input=[text], model=model)

        # Se for gerador, converta para lista para permitir indexação
        if isinstance(response, dict) and 'data' in response:
            embedding_data = response['data']
            if isinstance(embedding_data, list) and len(embedding_data) > 0:
                embedding = embedding_data[0].get('embedding', None)
                if embedding:
                    logger.debug("Embedding gerada com sucesso.")
                    return embedding
                else:
                    logger.error("Nenhuma embedding encontrada no resultado.")
                    return None
        else:
            logger.error("Resposta inesperada da API de embeddings.")
            return None
    except Exception as e:
        logger.error(f"Erro ao gerar embeddings: {e}")
        return None

def process_pdf_embeddings():
    """Processa embeddings para PDFs modificados ou novos."""
    logger.info("Iniciando o processamento de PDFs para geração de embeddings...")
    pdf_texts = load_and_process_pdfs()
    logger.debug(f"PDFs processados: {pdf_texts}")
    if not pdf_texts:
        logger.info("Nenhum PDF novo ou modificado encontrado.")
        return
    for pdf_name, text in pdf_texts.items():
        logger.info(f"Processando o arquivo PDF: {pdf_name}")
        embedding = generate_embedding(text)
        if embedding:
            save_embedding(pdf_name, embedding)

def save_embedding(pdf_name, embedding):
    """Salva embeddings em um arquivo .json."""
    embedding_path = os.path.join(EMBEDDINGS_DIRECTORY, f"{pdf_name}.json")
    logger.info(f"Salvando embedding no arquivo: {embedding_path}")
    with open(embedding_path, "w") as f:
        json.dump({"embedding": embedding}, f)
    logger.debug(f"Embedding salva com sucesso para o arquivo {pdf_name}.")

# Bloco de inicialização
if __name__ == "__main__":
    logger.info("Iniciando o processo de geração de embeddings...")
    process_pdf_embeddings()
    logger.info("Processo de geração de embeddings finalizado.")
