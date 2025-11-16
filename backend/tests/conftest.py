#? <|------------------- Configuración de pytest y fixtures para testing -------------------|>
"""
* Configuración centralizada de pruebas con pytest
* 
* Fixtures disponibles:
* - app: Aplicación Flask configurada para testing
* - client: Cliente HTTP para hacer requests de prueba
* - mongo_test: Mock de MongoDB para tests sin conexión real
* - paciente_ejemplo: Datos de ejemplo para crear pacientes
* 
* Estos fixtures se inyectan automáticamente en las funciones de test
"""

import pytest
import sys
import os
from pathlib import Path

#* Agregar el directorio backend al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from app import app as flask_app


#? <|------------------- Fixture de aplicación Flask -------------------|>

#? <|------------------- Fixture de aplicación Flask -------------------|>

@pytest.fixture
def app():
    """
    * Fixture que provee la aplicación Flask configurada para testing
    * 
    * Activa el modo TESTING para deshabilitar propagación de errores
    * y permitir mejor debugging
    * 
    * Returns:
    *     Flask: Aplicación Flask en modo testing
    """
    flask_app.config['TESTING'] = True
    return flask_app


#? <|------------------- Fixture de cliente HTTP -------------------|>

#? <|------------------- Fixture de cliente HTTP -------------------|>

@pytest.fixture
def client(app):
    """
    * Fixture que provee un cliente de prueba para hacer requests HTTP
    * 
    * Permite simular peticiones GET, POST, PUT, DELETE sin servidor real
    * 
    * Args:
    *     app: Fixture de aplicación Flask
    * 
    * Returns:
    *     FlaskClient: Cliente de testing para hacer requests
    """
    return app.test_client()


#? <|------------------- Fixture de MongoDB Mock -------------------|>

#? <|------------------- Fixture de MongoDB Mock -------------------|>

@pytest.fixture
def mongo_test(monkeypatch):
    """
    * Fixture que provee una colección MongoDB mock para testing
    * 
    * Simula operaciones de MongoDB sin conexión real a la base de datos
    * Ideal para testing rápido y sin dependencias externas
    * 
    * Operaciones soportadas:
    * - insert_one: Insertar documentos
    * - find_one: Buscar un documento
    * - find: Buscar múltiples documentos
    * - update_one: Actualizar un documento
    * - count_documents: Contar documentos
    * - aggregate: Agregaciones (mock simple)
    * 
    * Yields:
    *     Mock collection con métodos básicos de MongoDB
    """
    #! ||------------------- Mock para evitar problemas SSL con Python 3.12 -------------------||
    
    class MockCollection:
        """
        * Colección mock que simula operaciones de MongoDB en memoria
        * 
        * Almacena documentos en un diccionario para evitar dependencia de MongoDB real
        """
        def __init__(self):
            self.data = {}  #* Diccionario para almacenar documentos (key: id, value: documento)
            self.counter = 1  #* Contador para generar IDs únicos
        
        def insert_one(self, document):
            """* Simula inserción de documento en MongoDB"""
            from bson import ObjectId
            doc_id = ObjectId()
            document['_id'] = doc_id
            self.data[str(doc_id)] = document
            
            class InsertResult:
                """* Resultado de inserción mock"""
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            
            return InsertResult(doc_id)
        
        def find_one(self, query):
            """* Simula búsqueda de un documento"""
            if '_id' in query:
                doc_id = str(query['_id'])
                return self.data.get(doc_id)
            #* Buscar por otros campos
            for doc in self.data.values():
                match = True
                for key, value in query.items():
                    if doc.get(key) != value:
                        match = False
                        break
                if match:
                    return doc
            return None
        
        def find(self, query):
            """* Simula búsqueda de múltiples documentos"""
            results = []
            for doc in self.data.values():
                match = True
                for key, value in query.items():
                    if doc.get(key) != value:
                        match = False
                        break
                if match:
                    results.append(doc)
            return results
        
        def count_documents(self, query):
            """* Simula conteo de documentos"""
            return len(self.find(query))
        
        def update_one(self, query, update):
            """* Simula actualización de un documento"""
            doc = self.find_one(query)
            if doc:
                if '$set' in update:
                    doc.update(update['$set'])
                
                class UpdateResult:
                    """* Resultado de actualización mock"""
                    def __init__(self, matched):
                        self.matched_count = matched
                        self.modified_count = matched
                
                return UpdateResult(1)
            
            class UpdateResult:
                """* Resultado cuando no se encuentra documento"""
                def __init__(self, matched):
                    self.matched_count = matched
                    self.modified_count = 0
            
            return UpdateResult(0)
        
        def aggregate(self, pipeline):
            """* Simula agregación de MongoDB (retorna vacío)"""
            return []
        
        def delete_many(self, query):
            """* Simula eliminación de documentos"""
            pass
    
    #* Crear instancia del mock
    mock_collection = MockCollection()
    
    #* Parchear el módulo database.mongo_db para usar el mock
    import database.mongo_db as mongo_module
    original_get_collection = mongo_module.get_collection
    
    def mock_get_collection():
        """* Retorna colección mock en lugar de la real"""
        return mock_collection
    
    monkeypatch.setattr(mongo_module, 'get_collection', mock_get_collection)
    
    #* Parchear también el módulo app
    import app
    def mock_get_db_collection():
        """* Retorna colección mock para app.py"""
        return mock_collection
    
    monkeypatch.setattr(app, 'get_db_collection', mock_get_db_collection)
    
    #* Retornar mock para uso en tests
    yield mock_collection


#? <|------------------- Fixture de datos de ejemplo -------------------|>

@pytest.fixture
def paciente_ejemplo():
    """
    * Fixture que provee datos de ejemplo para crear un paciente
    * 
    * Incluye todos los campos necesarios para crear un paciente completo:
    * - Datos personales
    * - Dirección completa
    * - Información del estudio
    * 
    * Returns:
    *     dict: Datos de paciente válidos listos para usar
    """
    return {
        'datos_personales': {
            'nombre': 'Test',
            'apellido_paterno': 'Paciente',
            'apellido_materno': 'Ejemplo',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'telefono': '6641234567',
            'email': 'test@example.com'
        },
        'direccion': {
            'codigo_postal': '22000',
            'colonia': 'Centro',
            'municipio': 'Tijuana',
            'estado': 'Baja California',
            'calle': 'Av. Revolución',
            'numero_exterior': '123',
            'numero_interior': '',
            'referencias': 'Cerca del centro'
        },
        'estudio': {
            'tipo': 'biometria_hematica',
            'notas': 'Paciente de prueba para testing'
        }
    }