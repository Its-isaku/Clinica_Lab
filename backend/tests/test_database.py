"""
Tests para la conexión y operaciones de MongoDB

Tests incluidos:
1. test_conexion_mongodb - Verificar que la conexión funciona
2. test_insertar_documento - Verificar inserción en MongoDB
"""

import pytest
from database import get_collection


def test_conexion_mongodb():
    """
    Test 10: Verificar que la conexión a MongoDB funciona
    
    Condiciones:
    - La colección debe existir
    - Debe poder hacer operaciones básicas
    """
    collection = get_collection()
    
    assert collection is not None, "La colección no debe ser None"
    
    # Verificar que podemos hacer un count
    count = collection.count_documents({})
    assert count >= 0, "El count debe ser >= 0"


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