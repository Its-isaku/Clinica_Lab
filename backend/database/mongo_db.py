#? <|------------------- Módulo de conexión y gestión de MongoDB Atlas -------------------|>
"""
* Manejo de conexión a MongoDB con patrón Singleton
* 
* Características:
* - Lazy loading de conexiones (solo se conecta cuando es necesario)
* - Configuración TLS/SSL segura
* - Timeouts configurados para evitar bloqueos
* - Funciones de utilidad para testing
"""
#! ||------------------- Importante: Configuración TLS permite certificados inválidos -------------------||

import sys
from pathlib import Path

#* Agregar directorio padre al path para importar módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))
from pymongo import MongoClient
from config import Config

#? <|------------------- Variables globales para patrón Singleton -------------------|>

#* Instancias globales con lazy loading (None hasta que se requieran)
_client = None
_db = None
_collection = None


#? <|------------------- Funciones de acceso con Lazy Loading -------------------|>

def get_client():
    """
    * Obtiene o crea el cliente de MongoDB con configuración TLS segura
    * 
    * Implementa patrón Singleton: solo crea una instancia del cliente
    * 
    * Configuración:
    *     - serverSelectionTimeoutMS: 5000ms (timeout para seleccionar servidor)
    *     - connectTimeoutMS: 5000ms (timeout para establecer conexión)
    *     - tls: True (conexión segura)
    *     - tlsAllowInvalidCertificates: True (permite certificados autofirmados)
    *     - tlsAllowInvalidHostnames: True (permite hostnames no coincidentes)
    * 
    * Returns:
    *     MongoClient: Cliente de MongoDB configurado y conectado
    """
    #! ||------------------- Configuración TLS relajada - Solo para desarrollo -------------------||
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
    """
    * Obtiene o crea la base de datos con lazy loading
    * 
    * Returns:
    *     Database: Base de datos de laboratorio clínico
    """
    global _db
    if _db is None:
        _db = get_client()[Config.DATABASE_NAME]
    return _db


def get_collection():
    """
    * Retorna la colección de pacientes con lazy loading
    * 
    * Esta es la función principal que usa la aplicación
    * 
    * Returns:
    *     Collection: Colección de pacientes en MongoDB
    """
    global _collection
    if _collection is None:
        _collection = get_db()[Config.COLLECTION_NAME]
    return _collection


#? <|------------------- Función de utilidad para testing -------------------|>

def test_connection():
    """
    * Prueba la conexión a MongoDB usando comando ping
    * 
    * Returns:
    *     bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        client = get_client()
        client.admin.command('ping')
        return True
    except Exception as e:
        return False


#? <|------------------- Ejecución directa para testing -------------------|>

if __name__ == '__main__':
    #* Ejecutar test de conexión cuando se ejecuta el módulo directamente
    test_connection()