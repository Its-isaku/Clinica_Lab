#? <|------------------- Tests para los endpoints de la API REST -------------------|>
"""
* Suite de pruebas para todos los endpoints HTTP de la API
* 
* Tests incluidos:
* 1. test_get_estadisticas - GET /api/estadisticas
* 2. test_get_pacientes - GET /api/pacientes
* 3. test_create_paciente - POST /api/pacientes
* 4. test_api_codigo_postal_endpoint - GET /api-externa/cp/{codigo}
* 5. test_api_codigo_postal_invalido - Validar error con CP inválido
* 
* Valida respuestas HTTP, estructura de datos y manejo de errores
"""

import pytest
import json


#? <|------------------- Test de endpoint de estadísticas -------------------|>

def test_get_estadisticas(client, mongo_test):
    """
    * Test 5: Verificar endpoint de estadísticas del dashboard
    * 
    * Valida que retorna:
    * - total_pacientes: Cantidad de pacientes activos
    * - estudios_hoy: Estudios realizados el día de hoy
    * - por_tipo_estudio: Distribución por tipo de estudio
    * 
    * Código esperado: 200 OK
    """
    #* Hacer petición GET al endpoint de estadísticas
    response = client.get('/api/estadisticas')
    
    #* Validar código de respuesta exitoso
    assert response.status_code == 200
    data = response.get_json()
    
    #* Validar que contiene todos los campos requeridos
    assert 'total_pacientes' in data
    assert 'estudios_hoy' in data
    assert 'por_tipo_estudio' in data


#? <|------------------- Test de endpoint listar pacientes -------------------|>

def test_get_pacientes(client, mongo_test):
    """
    * Test 6: Verificar endpoint de listar pacientes
    * 
    * CORRECCIÓN IMPORTANTE:
    * GET debe retornar 200 (OK), NO 201 (Created)
    * 201 es solo para POST cuando se crea un recurso
    * 
    * Valida:
    * - Status code 200
    * - Respuesta contiene 'pacientes' y 'total'
    """
    #* Hacer petición GET para listar todos los pacientes
    response = client.get('/api/pacientes')
    
    #* Validar código de respuesta correcto (200 para GET)
    assert response.status_code == 200, f"Se esperaba 200, se obtuvo {response.status_code}"
    
    #* Validar estructura de la respuesta
    data = response.get_json()
    assert 'pacientes' in data
    assert 'total' in data


#? <|------------------- Test de creación de paciente -------------------|>

def test_create_paciente(client, paciente_ejemplo, mongo_test):
    """
    * Test 7: Verificar creación de paciente con generación de resultados
    * 
    * Valida:
    * - Paciente se crea en la base de datos
    * - Se generan automáticamente 15 resultados
    * - Retorna status 201 (Created)
    * - Respuesta incluye paciente completo con resultados
    """
    #* Enviar petición POST con datos del paciente en formato JSON
    response = client.post(
        '/api/pacientes',
        data=json.dumps(paciente_ejemplo),
        content_type='application/json'
    )
    
    #* Validar código de respuesta (201 Created)
    assert response.status_code == 201
    data = response.get_json()
    
    #* Validar estructura de la respuesta
    assert 'message' in data
    assert 'paciente' in data
    
    #* Validar que se generaron automáticamente 15 resultados
    paciente = data['paciente']
    assert 'resultados' in paciente
    assert len(paciente['resultados']) == 15


#? <|------------------- Test de API externa código postal -------------------|>

def test_api_codigo_postal_endpoint(client):
    """
    * Test 8: Verificar endpoint de código postal (API externa)
    * 
    * Valida integración con API de Copomex
    * 
    * Acepta:
    * - 200: API externa responde correctamente
    * - 400: API externa no disponible o error
    """
    #* Consultar código postal de Tijuana
    response = client.get('/api-externa/cp/22000')
    
    #* Aceptar tanto éxito como error (depende de API externa)
    assert response.status_code in [200, 400]
    
    #* Validar estructura de respuesta si fue exitosa
    if response.status_code == 200:
        data = response.get_json()
        assert 'colonias' in data or 'error' in data


#? <|------------------- Test de validación de código postal -------------------|>

def test_api_codigo_postal_invalido(client):
    """
    * Test 9: Verificar que CP inválido retorna error 400
    * 
    * CORRECCIÓN IMPORTANTE:
    * El endpoint valida entrada ANTES de procesar
    * Por lo tanto retorna 400 (Bad Request), NO 500 (Server Error)
    * 
    * Valida:
    * - Status code 400 para entrada inválida
    * - Mensaje de error en respuesta
    """
    #* Enviar código postal inválido (letras en lugar de números)
    response = client.get('/api-externa/cp/abc')
    
    #* Validar que retorna Bad Request (400), no Server Error (500)
    assert response.status_code == 400, f"Se esperaba 400, se obtuvo {response.status_code}"
    
    #* Validar que incluye mensaje de error
    data = response.get_json()
    assert 'error' in data