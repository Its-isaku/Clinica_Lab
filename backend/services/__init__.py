#? <|------------------- Módulo services - Exportación de servicios -------------------|>
"""
* Punto de entrada del paquete services
* 
* Exporta los servicios principales del backend:
* - generador_resultados: Generación de resultados clínicos aleatorios
* - api_service: Integración con API externa de códigos postales
* 
* Funciones disponibles:
* - generar_resultados: Genera 15 resultados según tipo de estudio
* - obtener_nombre_estudio: Convierte código a nombre completo
* - obtener_info_codigo_postal: Consulta CP en API Copomex
* - APIException: Excepción para errores de API externa
"""

from .generador_resultados import generar_resultados, obtener_nombre_estudio
from .api_service import obtener_info_codigo_postal, APIException

#* Lista de símbolos públicos exportados por este módulo
__all__ = [
    'generar_resultados',
    'obtener_nombre_estudio',
    'obtener_info_codigo_postal',
    'APIException'
]