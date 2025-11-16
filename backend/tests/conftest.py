"""
Configuración de pytest y fixtures para testing

Fixtures disponibles:
- app: Aplicación Flask de prueba
- client: Cliente de prueba para hacer requests
- mongo_test: Conexión a MongoDB de prueba
- paciente_ejemplo: Datos de ejemplo para crear pacientes
"""

import pytest
import sys
import os
from pathlib import Path

# Agregar el directorio backend al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from app import app as flask_app


@pytest.fixture
def app():
    """
    Fixture que provee la aplicación Flask configurada para testing
    
    Returns:
        Flask: Aplicación Flask en modo testing
    """
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """
    Fixture que provee un cliente de prueba para hacer requests HTTP
    
    Args:
        app: Fixture de aplicación Flask
    
    Returns:
        FlaskClient: Cliente de testing
    """
    return app.test_client()


@pytest.fixture
def mongo_test(monkeypatch):
    """
    Fixture que provee una colección MongoDB mock para testing
    
    Ya que Python 3.12 tiene problemas SSL con MongoDB Atlas,
    usamos un mock para los tests
    
    Yields:
        Mock collection con métodos básicos
    """
    class MockCollection:
        def __init__(self):
            self.data = {}
            self.counter = 1
        
        def insert_one(self, document):
            from bson import ObjectId
            doc_id = ObjectId()
            document['_id'] = doc_id
            self.data[str(doc_id)] = document
            
            class InsertResult:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            
            return InsertResult(doc_id)
        
        def find_one(self, query):
            if '_id' in query:
                doc_id = str(query['_id'])
                return self.data.get(doc_id)
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
            return len(self.find(query))
        
        def update_one(self, query, update):
            doc = self.find_one(query)
            if doc:
                if '$set' in update:
                    doc.update(update['$set'])
                
                class UpdateResult:
                    def __init__(self, matched):
                        self.matched_count = matched
                        self.modified_count = matched
                
                return UpdateResult(1)
            
            class UpdateResult:
                def __init__(self, matched):
                    self.matched_count = matched
                    self.modified_count = 0
            
            return UpdateResult(0)
        
        def aggregate(self, pipeline):
            # Simple mock - just return empty results
            return []
        
        def delete_many(self, query):
            pass
    
    mock_collection = MockCollection()
    
    # Patch at database.mongo_db module level
    import database.mongo_db as mongo_module
    original_get_collection = mongo_module.get_collection
    
    def mock_get_collection():
        return mock_collection
    
    monkeypatch.setattr(mongo_module, 'get_collection', mock_get_collection)
    
    # Also patch in app module
    import app
    def mock_get_db_collection():
        return mock_collection
    
    monkeypatch.setattr(app, 'get_db_collection', mock_get_db_collection)
    
    yield mock_collection


@pytest.fixture
def paciente_ejemplo():
    """
    Fixture que provee datos de ejemplo para crear un paciente
    
    Returns:
        dict: Datos de paciente válidos
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