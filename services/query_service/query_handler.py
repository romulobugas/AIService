# query_service/query_handler.py

import os
import json
import numpy as np
import openai  # Integração com o modelo Llama
from services.pdf_service.embedding_service import generate_embedding
from config.logging_config import logger

EMBEDDINGS_DIRECTORY = "data/embeddings/"
SIMILARITY_THRESHOLD = 0.3  # Threshold para filtrar perguntas irrelevantes

# Configuração do cliente OpenAI com Llama
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"

def load_embeddings():
    """Carrega as embeddings dos PDFs salvas em arquivos .json."""
    logger.info(f"Carregando embeddings dos arquivos JSON no diretório: {EMBEDDINGS_DIRECTORY}")
    embeddings = {}

    if not os.path.exists(EMBEDDINGS_DIRECTORY):
        logger.error(f"Diretório de embeddings não encontrado: {EMBEDDINGS_DIRECTORY}")
        return embeddings

    for filename in os.listdir(EMBEDDINGS_DIRECTORY):
        if filename.endswith(".json"):
            file_path = os.path.join(EMBEDDINGS_DIRECTORY, filename)
            logger.debug(f"Carregando embedding de {filename}")
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if "embedding" in data:
                        embeddings[filename] = np.array(data["embedding"])
                    else:
                        logger.warning(f"Arquivo {filename} não contém o campo 'embedding'. Ignorado.")
            except Exception as e:
                logger.error(f"Erro ao carregar embedding de {filename}: {e}")

    logger.info(f"Embeddings carregadas com sucesso. Total de arquivos processados: {len(embeddings)}")
    return embeddings

def cosine_similarity(vec1, vec2):
    """Calcula a similaridade de cosseno entre dois vetores."""
    try:
        logger.debug("Calculando a similaridade de cosseno.")
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    except Exception as e:
        logger.error(f"Erro ao calcular a similaridade de cosseno: {e}")
        return 0  # Retorna 0 se houver erro

def find_best_match(query, document_embeddings):
    """Encontra a melhor correspondência entre a query e os documentos."""
    try:
        logger.info(f"Gerando embedding para a consulta: '{query}'")
        query_embedding = generate_embedding(query)  # Gera a embedding da pergunta
        if query_embedding is None:
            logger.error("Falha ao gerar embedding da consulta.")
            return None, -1  # Retorna sem correspondência se não for possível gerar a embedding

        best_match = None
        highest_similarity = -1

        logger.info("Comparando a consulta com as embeddings dos documentos...")
        for doc_name, embedding in document_embeddings.items():
            similarity = cosine_similarity(query_embedding, embedding)
            logger.debug(f"Similaridade com {doc_name}: {similarity}")

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = doc_name

        logger.info(f"Melhor correspondência: {best_match} com similaridade de {highest_similarity}")
        return best_match, highest_similarity

    except Exception as e:
        logger.error(f"Erro ao encontrar a melhor correspondência: {e}")
        return None, -1  # Em caso de erro, retorne sem correspondência

def generate_llama_response(content):
    """Usa o modelo Llama para gerar uma resposta aprimorada com base no conteúdo."""
    try:
        logger.info("Enviando o conteúdo ao Llama para melhorar a resposta...")
        response = openai.Completion.create(
            model="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            prompt=f"Baseado nas informações a seguir, gere uma resposta clara e concisa para o usuário: {content}",
            max_tokens=150
        )

        # Verificar se a resposta é do tipo esperado
        if isinstance(response, dict) and 'choices' in response:
            choices = response['choices']
            if isinstance(choices, list) and len(choices) > 0:
                return choices[0].get('text', content)  # Retorna a resposta ou o conteúdo original
            else:
                logger.error("Nenhuma escolha disponível na resposta.")
                return content
        else:
            logger.error("Resposta inesperada da API Llama.")
            return content

    except Exception as e:
        logger.error(f"Erro ao gerar resposta com Llama: {e}")
        return content  # Se ocorrer um erro, retorna o conteúdo original

def extract_relevant_section(document_text, query):
    """Simula a extração de um trecho relevante do texto."""
    logger.info("Extraindo um trecho relevante do documento.")
    # Retorna o primeiro parágrafo como um exemplo
    return document_text.split(".")[0] + "."

def process_query(query, embeddings):
    """Processa a consulta para buscar a melhor correspondência e melhorar a resposta."""
    best_match, similarity = find_best_match(query, embeddings)

    # Verificar se a similaridade é baixa
    if similarity < SIMILARITY_THRESHOLD:
        logger.info(f"Consulta '{query}' não é relevante. Similaridade: {similarity}")
        return "Este assistente só responde perguntas relacionadas ao WMS."

    # Carregar o conteúdo do documento correspondente
    if best_match:
        document_path = os.path.join(EMBEDDINGS_DIRECTORY, best_match)
        if os.path.exists(document_path):
            logger.info(f"Melhor correspondência encontrada: {best_match} com similaridade de {similarity}")
            try:
                with open(document_path, "r") as f:
                    document_data = json.load(f)
                    document_text = document_data.get("content", "Sem conteúdo disponível.")
            except Exception as e:
                logger.error(f"Erro ao carregar o conteúdo do documento: {e}")
                return "Erro ao carregar o documento."

            # Extrair um trecho relevante do texto
            relevant_section = extract_relevant_section(document_text, query)

            # Melhorar a resposta com Llama
            improved_response = generate_llama_response(relevant_section)
            return improved_response
        else:
            logger.error(f"O arquivo {document_path} não existe.")
            return "Erro: Documento não encontrado."

    logger.error("Nenhuma correspondência encontrada.")
    return "Nenhuma correspondência relevante foi encontrada."
