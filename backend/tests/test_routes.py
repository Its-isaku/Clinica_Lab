"""
Tests para los endpoints de la API REST

Tests incluidos:
1. test_get_estadisticas - GET /api/estadisticas
2. test_get_pacientes - GET /api/pacientes
3. test_create_paciente - POST /api/pacientes
4. test_api_codigo_postal_endpoint - GET /api-externa/cp/{codigo}
5. test_api_codigo_postal_invalido - Validar error con CP inválido
"""

import pytest
import json


def test_get_estadisticas(client):
    """
    Test 5: Verificar endpoint de estadísticas
    
    Debe retornar:
    - total_pacientes
    - estudios_hoy
    - por_tipo_estudio
    """
    response = client.get('/api/estadisticas')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'total_pacientes' in data
    assert 'estudios_hoy' in data
    assert 'por_tipo_estudio' in data


def test_get_pacientes(client):
    """
    Test 6: Verificar endpoint de listar pacientes
    
    CORRECCIÓN: GET debe retornar 200, no 201
    """
    response = client.get('/api/pacientes')
    
    # CORREGIDO: GET retorna 200
    assert response.status_code == 200, f"Se esperaba 200, se obtuvo {response.status_code}"
    
    data = response.get_json()
    assert 'pacientes' in data
    assert 'total' in data


def test_create_paciente(client, paciente_ejemplo):
    """
    Test 7: Verificar creación de paciente
    
    Debe:
    - Crear el paciente en la base de datos
    - Generar 15 resultados automáticamente
    - Retornar status 201
    """
    response = client.post(
        '/api/pacientes',
        data=json.dumps(paciente_ejemplo),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert 'message' in data
    assert 'paciente' in data
    
    # Verificar que se generaron resultados
    paciente = data['paciente']
    assert 'resultados' in paciente
    assert len(paciente['resultados']) == 15


def test_api_codigo_postal_endpoint(client):
    """
    Test 8: Verificar endpoint de código postal
    
    Este test puede fallar si la API externa está caída
    """
    response = client.get('/api-externa/cp/22000')
    
    # Aceptar tanto 200 (éxito) como 400 (API caída)
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.get_json()
        assert 'colonias' in data or 'error' in data


def test_api_codigo_postal_invalido(client):
    """
    Test 9: Verificar que CP inválido retorna error 400
    
    El endpoint valida correctamente y retorna 400 para entradas inválidas
    """
    # CP inválido (no es de 5 dígitos)
    response = client.get('/api-externa/cp/abc')
    
    # Debe retornar 400 (Bad Request) para CP inválido
    assert response.status_code == 400, f"Se esperaba 400, se obtuvo {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data