"""
Script de Perfilado de Rendimiento
Herramientas: cProfile, timeit

Analiza el rendimiento de:
- Endpoints de la API
- Generación de resultados médicos
- Consultas a MongoDB
- Llamadas a API externa
"""

import cProfile
import pstats
import io
import timeit
import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from services.generador_resultados import generar_resultados
from database.mongo_db import get_collection
from services.api_service import obtener_info_codigo_postal


# ========== CONFIGURACIÓN ==========
RUNS = 100  # Número de ejecuciones para timeit


def profile_with_cprofile(func, *args, **kwargs):
    """
    Perfila una función usando cProfile
    
    Args:
        func: Función a perfilar
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre
    
    Returns:
        tuple: (resultado, stats_string)
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Capturar estadísticas en un string
    string_buffer = io.StringIO()
    stats = pstats.Stats(profiler, stream=string_buffer)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 funciones más lentas
    
    return result, string_buffer.getvalue()


def measure_with_timeit(func, *args, **kwargs):
    """
    Mide el tiempo de ejecución promedio usando timeit
    
    Args:
        func: Función a medir
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre
    
    Returns:
        float: Tiempo promedio en segundos
    """
    def wrapper():
        return func(*args, **kwargs)
    
    total_time = timeit.timeit(wrapper, number=RUNS)
    avg_time = total_time / RUNS
    
    return avg_time


# ========== TESTS DE RENDIMIENTO ==========

def test_generar_resultados_biometria():
    """Test 1: Generación de resultados de Biometría Hemática"""
    print("\n" + "="*80)
    print("TEST 1: Generación de Resultados - Biometría Hemática")
    print("="*80)
    
    # cProfile
    print("\n--- cProfile (análisis detallado) ---")
    result, stats = profile_with_cprofile(generar_resultados, 'biometria_hematica', 'M')
    print(f"Resultados generados: {len(result)} parámetros")
    print(stats[:1500])  # Imprimir primeros 1500 caracteres
    
    # timeit
    print("\n--- timeit (tiempo promedio) ---")
    avg_time = measure_with_timeit(generar_resultados, 'biometria_hematica', 'M')
    print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")


def test_generar_resultados_quimica():
    """Test 2: Generación de resultados de Química Sanguínea"""
    print("\n" + "="*80)
    print("TEST 2: Generación de Resultados - Química Sanguínea")
    print("="*80)
    
    # timeit
    avg_time = measure_with_timeit(generar_resultados, 'quimica_sanguinea', 'F')
    print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")


def test_generar_resultados_orina():
    """Test 3: Generación de resultados de Examen de Orina"""
    print("\n" + "="*80)
    print("TEST 3: Generación de Resultados - Examen de Orina")
    print("="*80)
    
    # timeit
    avg_time = measure_with_timeit(generar_resultados, 'examen_orina', 'M')
    print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")


def test_mongodb_query():
    """Test 4: Consulta a MongoDB (count_documents)"""
    print("\n" + "="*80)
    print("TEST 4: Consulta MongoDB - count_documents")
    print("="*80)
    
    try:
        collection = get_collection()
        
        # Probar conexión primero
        test_count = collection.count_documents({})
        
        # cProfile
        print("\n--- cProfile (análisis detallado) ---")
        result, stats = profile_with_cprofile(collection.count_documents, {})
        print(f"Total de documentos: {result}")
        print(stats[:1500])
        
        # timeit
        print("\n--- timeit (tiempo promedio) ---")
        avg_time = measure_with_timeit(collection.count_documents, {})
        print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")
        
    except Exception as e:
        print(f"⚠️  SKIP: MongoDB no disponible ({str(e)[:100]})")
        print("Esto no afecta las métricas de generación de resultados")


def test_mongodb_find():
    """Test 5: Consulta MongoDB (find con limit)"""
    print("\n" + "="*80)
    print("TEST 5: Consulta MongoDB - find con limit")
    print("="*80)
    
    try:
        collection = get_collection()
        
        def find_limited():
            return list(collection.find().limit(10))
        
        # timeit
        avg_time = measure_with_timeit(find_limited)
        print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")
        
    except Exception as e:
        print(f"⚠️  SKIP: MongoDB no disponible")


def test_api_copomex():
    """Test 6: Llamada a API externa (Copomex)"""
    print("\n" + "="*80)
    print("TEST 6: API Externa - Copomex")
    print("="*80)
    
    try:
        # Solo 10 ejecuciones para API externa
        total_time = 0
        runs = 10
        
        for i in range(runs):
            start = timeit.default_timer()
            obtener_info_codigo_postal('22000')
            end = timeit.default_timer()
            total_time += (end - start)
        
        avg_time = total_time / runs
        print(f"Tiempo promedio ({runs} ejecuciones): {avg_time*1000:.4f} ms")
        print("NOTA: API externa es naturalmente más lenta (red)")
        
    except Exception as e:
        print(f"⚠️  SKIP: API externa no disponible")


def test_endpoint_get_pacientes():
    """Test 7: Endpoint GET /api/pacientes"""
    print("\n" + "="*80)
    print("TEST 7: Endpoint GET /api/pacientes")
    print("="*80)
    
    try:
        with app.test_client() as client:
            def get_pacientes():
                return client.get('/api/pacientes')
            
            # Probar primero
            test_response = get_pacientes()
            
            if test_response.status_code == 200:
                # cProfile
                print("\n--- cProfile (análisis detallado) ---")
                result, stats = profile_with_cprofile(get_pacientes)
                print(f"Status Code: {result.status_code}")
                print(stats[:1500])
                
                # timeit
                print("\n--- timeit (tiempo promedio) ---")
                avg_time = measure_with_timeit(get_pacientes)
                print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")
            else:
                print(f"⚠️  SKIP: Endpoint retornó {test_response.status_code}")
                
    except Exception as e:
        print(f"⚠️  SKIP: Error al probar endpoint ({str(e)[:100]})")


def test_endpoint_get_estadisticas():
    """Test 8: Endpoint GET /api/estadisticas"""
    print("\n" + "="*80)
    print("TEST 8: Endpoint GET /api/estadisticas")
    print("="*80)
    
    try:
        with app.test_client() as client:
            def get_estadisticas():
                return client.get('/api/estadisticas')
            
            # Probar primero
            test_response = get_estadisticas()
            
            if test_response.status_code == 200:
                # timeit
                avg_time = measure_with_timeit(get_estadisticas)
                print(f"Tiempo promedio ({RUNS} ejecuciones): {avg_time*1000:.4f} ms")
            else:
                print(f"⚠️  SKIP: Endpoint retornó {test_response.status_code}")
                
    except Exception as e:
        print(f"⚠️  SKIP: Error al probar endpoint")


# ========== RESUMEN DE RESULTADOS ==========

def generar_resumen():
    """Genera un resumen de todos los tests"""
    print("\n" + "="*80)
    print("RESUMEN DE ANÁLISIS DE RENDIMIENTO")
    print("="*80)
    
    print("\nTests realizados:")
    print("1. ✓ Generación de Biometría Hemática")
    print("2. ✓ Generación de Química Sanguínea")
    print("3. ✓ Generación de Examen de Orina")
    print("4. ~ Consulta MongoDB count_documents (si disponible)")
    print("5. ~ Consulta MongoDB find con limit (si disponible)")
    print("6. ~ API Externa Copomex (si disponible)")
    print("7. ~ Endpoint GET /api/pacientes (si disponible)")
    print("8. ~ Endpoint GET /api/estadisticas (si disponible)")
    
    print("\nHerramientas utilizadas:")
    print("- cProfile: Análisis detallado de llamadas a funciones")
    print("- timeit: Medición precisa de tiempos de ejecución")
    
    print("\nMETRICAS PRINCIPALES (siempre disponibles):")
    print("- Generación de resultados médicos (3 tipos de estudios)")
    print("- Estas son las funciones críticas del sistema")
    
    print("\nNOTA: Los tests de MongoDB/API pueden fallar si no hay conexión")
    print("      Pero las métricas de generación de resultados siempre funcionan")


# ========== MAIN ==========

if __name__ == '__main__':
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "ANÁLISIS DE RENDIMIENTO - BACKEND" + " "*25 + "║")
    print("║" + " "*15 + "Sistema de Gestión de Laboratorio Clínico" + " "*22 + "║")
    print("╚" + "="*78 + "╝")
    
    # Ejecutar todos los tests
    test_generar_resultados_biometria()
    test_generar_resultados_quimica()
    test_generar_resultados_orina()
    test_mongodb_query()
    test_mongodb_find()
    test_api_copomex()
    test_endpoint_get_pacientes()
    test_endpoint_get_estadisticas()
    
    # Generar resumen
    generar_resumen()
    
    print("\n✓ Análisis completado")
    print("Guarda estos resultados para tu reporte técnico\n")