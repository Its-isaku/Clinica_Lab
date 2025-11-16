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
from pathlib import Path

# Agregar el directorio backend al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app as flask_app
from pymongo import MongoClient
from config import Config


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
def mongo_test():
    """
    Fixture que provee una conexión a MongoDB de prueba
    
    IMPORTANTE: Usa una base de datos separada para testing
    para no afectar los datos reales
    
    CORRECCIÓN: Agregados parámetros SSL/TLS para evitar errores de handshake
    
    Yields:
        Collection: Colección de pacientes para testing
    """
    # CORREGIDO: Agregar parámetros SSL/TLS a la URI
    uri = Config.MONGO_URI
    
    # Si la URI no tiene parámetros SSL, agregarlos
    if 'tls=' not in uri.lower() and 'ssl=' not in uri.lower():
        # Agregar parámetros SSL seguros para testing
        separator = '&' if '?' in uri else '?'
        uri = f"{uri}{separator}tls=true&tlsAllowInvalidCertificates=true"
    
    # Crear cliente de prueba con configuración SSL
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
        connectTimeoutMS=5000
    )
    
    db = client['test_laboratorio_clinico']  # Base de datos de TEST
    collection = db['pacientes_test']
    
    yield collection
    
    # Limpiar después de cada test
    try:
        collection.delete_many({})
    except Exception as e:
        print(f"Warning: No se pudo limpiar la colección de test: {e}")
    finally:
        client.close()


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
            'numero_exterior': '123'
        },
        'estudio': {
            'tipo': 'biometria_hematica',
            'notas': 'Paciente de prueba'
        }
    }