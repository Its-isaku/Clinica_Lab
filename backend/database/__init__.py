#? <|------------------- Módulo database - Exportación de funciones públicas -------------------|>
"""
* Punto de entrada del paquete database
* 
* Exporta las funciones principales de conexión a MongoDB:
* - get_client: Cliente de MongoDB
* - get_db: Base de datos
* - get_collection: Colección de pacientes
* - test_connection: Verificar conexión
"""

from .mongo_db import get_client, get_db, get_collection, test_connection

#* Lista de símbolos públicos exportados por este módulo
__all__ = ['get_client', 'get_db', 'get_collection', 'test_connection']