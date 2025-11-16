"""
Tests para la conexión y operaciones de MongoDB

Tests incluidos:
1. test_conexion_mongodb - Verificar que la colección funciona
2. test_insertar_documento - Verificar inserción en MongoDB
"""

import pytest


def test_conexion_mongodb(monkeypatch):
    """
    Test 10: Verificar que la función get_collection funciona
    
    Condiciones:
    - La función debe existir y ser callable
    """
    from database.mongo_db import get_collection
    
    # Mock the get_client to avoid real connection
    class MockClient:
        def __getitem__(self, key):
            return MockDB()
    
    class MockDB:
        def __getitem__(self, key):
            return MockCollection()
    
    class MockCollection:
        pass
    
    import database.mongo_db as mongo_module
    monkeypatch.setattr(mongo_module, '_client', MockClient())
    monkeypatch.setattr(mongo_module, '_db', MockDB())
    monkeypatch.setattr(mongo_module, '_collection', MockCollection())
    
    collection = get_collection()
    assert collection is not None, "La colección no debe ser None"


def test_insertar_documento(mongo_test, paciente_ejemplo):
    """
    Test 11: Verificar que se puede insertar un documento en MongoDB
    
    Condiciones:
    - El documento debe insertarse correctamente
    - Debe retornar un ID válido
    - Debe poder recuperarse el documento
    """
    # Agregar campos requeridos
    paciente_ejemplo['fecha_registro'] = '2025-11-15T12:00:00'
    paciente_ejemplo['activo'] = True
    
    # Insertar
    result = mongo_test.insert_one(paciente_ejemplo)
    
    assert result.inserted_id is not None, "Debe retornar un ID"
    
    # Verificar que se insertó
    doc = mongo_test.find_one({'_id': result.inserted_id})
    
    assert doc is not None, "El documento debe existir"
    assert doc['datos_personales']['nombre'] == 'Test'
    assert doc['activo'] == True