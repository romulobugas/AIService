# pdf_service/pdf_loader.py


import os
from PyPDF2 import PdfReader
from .metadata_manager import is_file_modified, update_file_metadata
from config.logging_config import logger  # Importando o logger

PDF_DIRECTORY = "data/pdfs/"

def extract_text_from_pdf(pdf_path):
    """Extrai o texto de um arquivo PDF."""
    logger.info(f"Extraindo texto do PDF: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    logger.debug(f"Texto extraído do PDF {pdf_path}: {text[:60]}...")
    return text

def load_and_process_pdfs():
    """Carrega PDFs e processa apenas os que foram modificados ou são novos."""
    logger.info(f"Verificando PDFs no diretório: {PDF_DIRECTORY}")
    pdf_texts = {}
    if not os.path.exists(PDF_DIRECTORY):
        logger.warning(f"O diretório {PDF_DIRECTORY} não existe.")
        return pdf_texts
    
    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIRECTORY, filename)
            if is_file_modified(pdf_path):
                logger.info(f"Arquivo modificado ou novo encontrado: {filename}")
                text = extract_text_from_pdf(pdf_path)
                pdf_texts[filename] = text
                update_file_metadata(pdf_path)
            else:
                logger.info(f"Arquivo {filename} não modificado, pulando.")
    
    logger.debug(f"PDFs carregados e processados: {list(pdf_texts.keys())}")
    return pdf_texts
