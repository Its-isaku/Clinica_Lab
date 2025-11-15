import sys
from pathlib import Path

# Agregar el directorio padre al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from config import Config

# Variables globales para conexión lazy
_client = None
_db = None
_collection = None


def get_client():
    """Obtiene o crea el cliente de MongoDB"""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_db():
    """Obtiene o crea la base de datos"""
    global _db
    if _db is None:
        _db = get_client()[Config.DATABASE_NAME]
    return _db


def get_collection():
    """
    Retorna la colección de pacientes
    
    Returns:
        Collection: Colección de MongoDB para pacientes
    """
    global _collection
    if _collection is None:
        _collection = get_db()[Config.COLLECTION_NAME]
    return _collection


def test_connection():
    """
    Prueba la conexión a MongoDB
    
    Returns:
        bool: True si la conexión es exitosa
    """
    try:
        # Ping a la base de datos
        client = get_client()
        client.admin.command('ping')
        print(f"✓ Conexión exitosa a MongoDB: {Config.DATABASE_NAME}")
        print(f"✓ URI: {Config.MONGO_URI[:30]}...")
        return True
    except Exception as e:
        print(f"✗ Error al conectar a MongoDB: {e}")
        print(f"✗ Verifica que:")
        print(f"  1. El cluster de MongoDB Atlas existe")
        print(f"  2. Las credenciales son correctas")
        print(f"  3. Tu IP está en la lista de acceso")
        print(f"  4. El hostname del cluster es correcto")
        return False


if __name__ == '__main__':
    # Prueba de conexión directa
    test_connection()