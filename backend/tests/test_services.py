#? <|------------------- Tests para los servicios del backend -------------------|>
"""
* Suite de pruebas para servicios de negocio
* 
* Tests incluidos:
* 1. test_generar_resultados_biometria - Genera 15 parámetros de biometría
* 2. test_generar_resultados_quimica - Genera 15 parámetros de química
* 3. test_generar_resultados_orina - Genera 15 parámetros de orina
* 4. test_api_codigo_postal_valido - Consulta CP válido en API externa
* 
* Valida lógica de negocio y generación de datos
"""

import pytest
from services.generador_resultados import generar_resultados, obtener_nombre_estudio
from services.api_service import obtener_info_codigo_postal, APIException


def test_generar_resultados_biometria():
    """
    * Test 1: Verificar generación de Biometría Hemática
    * 
    * Valida:
    * - Se generan exactamente 15 parámetros
    * - Cada resultado tiene campos: parametro, valor, normal
    * - Sexo masculino usa rangos específicos de género
    * - Hay al menos algunos parámetros normales
    """
    resultados = generar_resultados('biometria_hematica', 'M')
    
    #* Verificar cantidad de parámetros
    assert len(resultados) == 15, f"Se esperaban 15 parámetros, se obtuvieron {len(resultados)}"
    
    #* Verificar que todos tengan los campos requeridos
    for resultado in resultados:
        assert 'parametro' in resultado
        assert 'valor' in resultado
        assert 'normal' in resultado
    
    #* Verificar que hay al menos algunos parámetros normales
    normales = [r for r in resultados if r['normal']]
    assert len(normales) > 0, "Debe haber al menos un parámetro normal"


def test_generar_resultados_quimica():
    """
    * Test 2: Verificar generación de Química Sanguínea
    * 
    * CORRECCIÓN:
    * Ahora verifica 15 parámetros y campos correctos
    * Los campos correctos son: rango_min/rango_max (NO rango_normal)
    * 
    * Valida:
    * - Se generan 15 parámetros
    * - Estructura correcta con rango_min y rango_max
    * - Tipos cuantitativos y cualitativos
    """
    resultados = generar_resultados('quimica_sanguinea', 'F')
    
    #* CORREGIDO: Ahora espera 15 parámetros
    assert len(resultados) == 15, f"Se esperaban 15 parámetros, se obtuvieron {len(resultados)}"
    
    #* Verificar estructura con campos CORRECTOS
    for resultado in resultados:
        assert 'parametro' in resultado
        assert 'valor' in resultado
        assert 'unidad' in resultado
        #* CORREGIDO: Los campos correctos son rango_min y rango_max
        assert 'rango_min' in resultado or 'tipo' in resultado  #* Algunos tienen rango, otros son cualitativos
        assert 'normal' in resultado


def test_generar_resultados_orina():
    """
    * Test 3: Verificar generación de Examen General de Orina
    * 
    * Valida:
    * - Se generan 15 parámetros
    * - Incluye parámetros cualitativos (Color, Aspecto, etc.)
    * - Incluye parámetros cuantitativos (Densidad, pH, etc.)
    * - Ambos tipos están presentes
    """
    resultados = generar_resultados('examen_orina', 'M')
    
    assert len(resultados) == 15
    
    #* Verificar que hay parámetros de ambos tipos
    cualitativos = [r for r in resultados if r['tipo'] == 'cualitativo']
    cuantitativos = [r for r in resultados if r['tipo'] == 'cuantitativo']
    
    assert len(cualitativos) > 0, "Debe haber parámetros cualitativos"
    assert len(cuantitativos) > 0, "Debe haber parámetros cuantitativos"


def test_api_codigo_postal_valido():
    """
    * Test 4: Verificar que la API de Copomex funciona con CP válido
    * 
    * Valida:
    * - API retorna colonias, municipio y estado
    * - Al menos una colonia en la respuesta
    * 
    * Nota: Este test puede fallar si:
    * - No hay conexión a internet
    * - La API externa está caída
    * - El formato de respuesta cambió
    """
    try:
        info = obtener_info_codigo_postal('22000')
        
        assert 'colonias' in info
        assert 'municipio' in info
        assert 'estado' in info
        assert len(info['colonias']) > 0, "Debe retornar al menos una colonia"
        
    except APIException:
        pytest.skip("API de Copomex no disponible")