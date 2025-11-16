"""
Módulo para la conexión y manejo de MongoDB
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from config import Config

# Variables globales para lazy loading
_client = None
_db = None
_collection = None


def get_client():
    """
    Obtiene o crea el cliente de MongoDB con configuración TLS segura
    
    Returns:
        MongoClient: Cliente de MongoDB configurado
    """
    global _client
    if _client is None:
        _client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
    return _client


def get_db():
    """Obtiene o crea la base de datos con lazy loading"""
    global _db
    if _db is None:
        _db = get_client()[Config.DATABASE_NAME]
    return _db


def get_collection():
    """Retorna la colección de pacientes con lazy loading"""
    global _collection
    if _collection is None:
        _collection = get_db()[Config.COLLECTION_NAME]
    return _collection


def test_connection():
    """Prueba la conexión a MongoDB"""
    try:
        client = get_client()
        client.admin.command('ping')
        return True
    except Exception as e:
        return False


if __name__ == '__main__':
    test_connection()