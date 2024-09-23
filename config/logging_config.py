import logging
import os

# Diretório de logs
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "ai_service.log")

# Garantir que o diretório de logs exista
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Mudamos para DEBUG para capturar todos os logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log para o arquivo
        logging.StreamHandler()  # Log também no console
    ]
)

logger = logging.getLogger("AIServiceLogger")
