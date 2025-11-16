#? <|------------------- Tests para conexión y operaciones de MongoDB -------------------|>
"""
* Suite de pruebas para el módulo database
* 
* Tests incluidos:
* 1. test_conexion_mongodb - Verificar que get_collection funciona
* 2. test_insertar_documento - Verificar inserción en MongoDB
* 
* Utilizan mocks para evitar dependencia de conexión real
"""

import pytest


#? <|------------------- Test de conexión a MongoDB -------------------|>

def test_conexion_mongodb(monkeypatch):
    """
    * Test 10: Verificar que la función get_collection funciona correctamente
    * 
    * Valida:
    * - La función existe y es callable
    * - Retorna una colección válida (no None)
    * 
    * Usa monkeypatch para evitar conexión real a MongoDB
    """
    from database.mongo_db import get_collection
    
    #* Crear mocks para simular la jerarquía de MongoDB (Client -> DB -> Collection)
    class MockClient:
        #* Mock del cliente de MongoDB
        def __getitem__(self, key):
            return MockDB()
    
    class MockDB:
        #* Mock de la base de datos
        def __getitem__(self, key):
            return MockCollection()
    
    class MockCollection:
        #* Mock de la colección
        pass
    
    #* Parchear las variables globales del módulo mongo_db
    import database.mongo_db as mongo_module
    monkeypatch.setattr(mongo_module, '_client', MockClient())
    monkeypatch.setattr(mongo_module, '_db', MockDB())
    monkeypatch.setattr(mongo_module, '_collection', MockCollection())
    
    #* Ejecutar función y validar que retorna una colección válida
    collection = get_collection()
    assert collection is not None, "La colección no debe ser None"


#? <|------------------- Test de inserción de documentos -------------------|>

def test_insertar_documento(mongo_test, paciente_ejemplo):
    """
    * Test 11: Verificar que se puede insertar un documento en MongoDB
    * 
    * Valida:
    * - El documento se inserta correctamente
    * - Retorna un ID válido
    * - El documento puede recuperarse después de insertar
    * - Los datos se conservan correctamente
    """
    #* Agregar campos requeridos al documento de prueba
    paciente_ejemplo['fecha_registro'] = '2025-11-15T12:00:00'
    paciente_ejemplo['activo'] = True
    
    #* Insertar documento en la colección mock
    result = mongo_test.insert_one(paciente_ejemplo)
    
    #* Validar que retorna un ID de inserción
    assert result.inserted_id is not None, "Debe retornar un ID"
    
    #* Recuperar el documento insertado usando su ID
    doc = mongo_test.find_one({'_id': result.inserted_id})
    
    #* Validar que el documento existe y conserva los datos correctamente
    assert doc is not None, "El documento debe existir"
    assert doc['datos_personales']['nombre'] == 'Test'
    assert doc['activo'] == True