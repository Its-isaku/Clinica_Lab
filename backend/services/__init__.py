"""
Módulo de servicios del backend

Contiene:
- generador_resultados: Genera resultados aleatorios de estudios clínicos
- api_service: Integración con API externa de códigos postales
"""

from .generador_resultados import generar_resultados, obtener_nombre_estudio
from .api_service import obtener_info_codigo_postal, APIException

__all__ = [
    'generar_resultados',
    'obtener_nombre_estudio',
    'obtener_info_codigo_postal',
    'APIException'
]