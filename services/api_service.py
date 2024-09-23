# api_service.py
from flask import Flask, request, jsonify
from services.query_service.query_handler import find_best_match, load_embeddings  # Importando a função corretamente
from config.logging_config import logger

app = Flask(__name__)

@app.route("/api/query", methods=["POST"])
def query():
    try:
        data = request.get_json()
        question = data.get("question", None)

        if not question:
            logger.warning("Consulta recebida sem uma pergunta válida.")
            return jsonify({"error": "Pergunta não fornecida"}), 400

        logger.info(f"Pergunta recebida: '{question}'")

        # Carregar as embeddings dos PDFs
        embeddings = load_embeddings()
        if not embeddings:
            logger.error("Nenhuma embedding disponível para consulta.")
            return jsonify({"error": "Nenhuma embedding disponível para consulta"}), 500

        # Encontrar a melhor correspondência
        best_match, similarity = find_best_match(question, embeddings)

        if best_match:
            logger.info(f"Melhor correspondência: {best_match} com similaridade de {similarity}")
            return jsonify({"response": f"Documento correspondente: {best_match}"}), 200
        else:
            return jsonify({"response": "Nenhuma correspondência encontrada"}), 200

    except Exception as e:
        logger.error(f"Erro no processamento da consulta: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    logger.info("Iniciando o serviço de API.")
    app.run(host="0.0.0.0", port=8001)
