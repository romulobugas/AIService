# pdf_service/metadata_manager.py
import os
import json
import hashlib

METADATA_FILE = "data/embeddings/metadata.json"

def calculate_file_hash(file_path):
    """Calcula o hash SHA256 de um arquivo."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def load_metadata():
    """Carrega metadados de um arquivo JSON."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Salva os metadados no arquivo JSON."""
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

def is_file_modified(file_path):
    """Verifica se o arquivo foi modificado com base no hash."""
    metadata = load_metadata()
    file_hash = calculate_file_hash(file_path)
    if file_path in metadata:
        return metadata[file_path] != file_hash
    return True

def update_file_metadata(file_path):
    """Atualiza o hash do arquivo nos metadados."""
    metadata = load_metadata()
    metadata[file_path] = calculate_file_hash(file_path)
    save_metadata(metadata)
